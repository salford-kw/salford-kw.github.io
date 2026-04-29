import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { createProduct, deleteProduct, getProducts } from "./db";
import { storagePut } from "./storage";
import { z } from "zod";
import { TRPCError } from "@trpc/server";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  products: router({
    list: publicProcedure.query(async () => {
      return await getProducts();
    }),
    create: protectedProcedure
      .input(z.object({
        title: z.string().min(1, "عنوان المنتج مطلوب"),
        description: z.string().optional(),
        imageUrl: z.string().optional(),
        storageKey: z.string().optional(),
      }))
      .mutation(async ({ ctx, input }) => {
        if (ctx.user?.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "فقط المسؤول يمكنه إضافة منتجات" });
        }
        return await createProduct(input);
      }),
    delete: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ ctx, input }) => {
        if (ctx.user?.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "فقط المسؤول يمكنه حذف منتجات" });
        }
        return await deleteProduct(input.id);
      }),
    uploadImage: protectedProcedure
      .input(z.object({
        file: z.instanceof(Buffer),
        filename: z.string(),
      }))
      .mutation(async ({ ctx, input }) => {
        if (ctx.user?.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "فقط المسؤول يمكنه رفع الصور" });
        }

        try {
          const ext = input.filename.split(".").pop() || "jpg";
          const key = `products/${Date.now()}.${ext}`;
          const { url, key: storageKey } = await storagePut(key, input.file, `image/${ext}`);
          return { url, storageKey };
        } catch (error) {
          console.error("Image upload error:", error);
          throw new TRPCError({
            code: "INTERNAL_SERVER_ERROR",
            message: "فشل رفع الصورة",
          });
        }
      }),
  }),
});

export type AppRouter = typeof appRouter;
