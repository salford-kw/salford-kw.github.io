import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { trpc } from "@/lib/trpc";
import { Loader2, Plus, Trash2, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { toast } from "sonner";

export default function Dashboard() {
  const { user, logout, loading } = useAuth();
  const [, setLocation] = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
  });

  const { data: products = [], isLoading, refetch } = trpc.products.list.useQuery();
  const createMutation = trpc.products.create.useMutation();
  const uploadImageMutation = trpc.products.uploadImage.useMutation();
  const deleteMutation = trpc.products.delete.useMutation();

  // Handle authorization with useEffect
  useEffect(() => {
    if (!loading && (!user || user.role !== "admin")) {
      setLocation("/");
    }
  }, [user, loading, setLocation]);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // Not authorized
  if (!user || user.role !== "admin") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">غير مصرح</h1>
          <p className="text-muted-foreground mb-6">
            ليس لديك صلاحيات للوصول إلى هذه الصفحة
          </p>
          <Button onClick={() => setLocation("/")} className="bg-primary hover:bg-primary/90">
            العودة للرئيسية
          </Button>
        </div>
      </div>
    );
  }

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error("حجم الصورة يجب أن يكون أقل من 5MB");
        return;
      }

      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreviewImage(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim()) {
      toast.error("عنوان المنتج مطلوب");
      return;
    }

    try {
      let imageUrl: string | undefined;
      let storageKey: string | undefined;

      // Upload image if selected
      if (selectedFile) {
        const arrayBuffer = await selectedFile.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);
        const uploadResult = await uploadImageMutation.mutateAsync({
          file: buffer,
          filename: selectedFile.name,
        });
        imageUrl = uploadResult.url;
        storageKey = uploadResult.storageKey;
      }

      // Create product
      await createMutation.mutateAsync({
        title: formData.title,
        description: formData.description || undefined,
        imageUrl,
        storageKey,
      });

      toast.success("تم إضافة المنتج بنجاح");
      setFormData({ title: "", description: "" });
      setSelectedFile(null);
      setPreviewImage(null);
      setIsOpen(false);
      refetch();
    } catch (error) {
      toast.error("حدث خطأ في إضافة المنتج");
      console.error(error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("هل تريد حذف هذا المنتج؟")) return;

    try {
      await deleteMutation.mutateAsync({ id });
      toast.success("تم حذف المنتج بنجاح");
      refetch();
    } catch (error) {
      toast.error("حدث خطأ في حذف المنتج");
      console.error(error);
    }
  };

  const handleLogout = async () => {
    await logout();
    setLocation("/");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-primary/10 border-b border-border sticky top-0 z-40">
        <div className="container flex items-center justify-between h-16">
          <div>
            <h1 className="text-2xl font-bold text-primary">لوحة التحكم</h1>
            <p className="text-sm text-muted-foreground">إدارة المنتجات</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-semibold">{user.name}</p>
              <p className="text-sm text-muted-foreground">مسؤول</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="gap-2"
            >
              <LogOut className="w-4 h-4" />
              تسجيل الخروج
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        {/* Add Product Button */}
        <div className="mb-8">
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2 bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4" />
                إضافة منتج جديد
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>إضافة منتج جديد</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Title */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    عنوان المنتج *
                  </label>
                  <Input
                    placeholder="أدخل عنوان المنتج"
                    value={formData.title}
                    onChange={(e) =>
                      setFormData({ ...formData, title: e.target.value })
                    }
                    required
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    الوصف
                  </label>
                  <Textarea
                    placeholder="أدخل وصف المنتج"
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    rows={4}
                  />
                </div>

                {/* Image Upload */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    صورة المنتج
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageSelect}
                    className="block w-full text-sm text-muted-foreground
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-md file:border-0
                      file:text-sm file:font-semibold
                      file:bg-primary file:text-primary-foreground
                      hover:file:bg-primary/90"
                  />
                  {previewImage && (
                    <div className="mt-4">
                      <p className="text-sm font-medium mb-2">معاينة الصورة:</p>
                      <img
                        src={previewImage}
                        alt="Preview"
                        className="max-h-64 rounded-lg border border-border"
                      />
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <div className="flex gap-4 justify-end">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsOpen(false);
                      setFormData({ title: "", description: "" });
                      setSelectedFile(null);
                      setPreviewImage(null);
                    }}
                  >
                    إلغاء
                  </Button>
                  <Button
                    type="submit"
                    disabled={createMutation.isPending || uploadImageMutation.isPending}
                    className="bg-primary hover:bg-primary/90"
                  >
                    {createMutation.isPending || uploadImageMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        جاري الإضافة...
                      </>
                    ) : (
                      "إضافة المنتج"
                    )}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Products Table */}
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="px-6 py-4 text-right text-sm font-semibold">
                    الصورة
                  </th>
                  <th className="px-6 py-4 text-right text-sm font-semibold">
                    العنوان
                  </th>
                  <th className="px-6 py-4 text-right text-sm font-semibold">
                    الوصف
                  </th>
                  <th className="px-6 py-4 text-right text-sm font-semibold">
                    تاريخ الإنشاء
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold">
                    الإجراءات
                  </th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center">
                      <Loader2 className="w-6 h-6 animate-spin inline-block text-primary" />
                    </td>
                  </tr>
                ) : products.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                      لا توجد منتجات بعد
                    </td>
                  </tr>
                ) : (
                  products.map((product) => (
                    <tr
                      key={product.id}
                      className="border-b border-border hover:bg-muted/50 transition-colors"
                    >
                      <td className="px-6 py-4">
                        {product.imageUrl ? (
                          <img
                            src={product.imageUrl}
                            alt={product.title}
                            className="w-12 h-12 rounded object-cover"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">
                            بدون صورة
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 font-medium">{product.title}</td>
                      <td className="px-6 py-4 text-muted-foreground max-w-xs truncate">
                        {product.description || "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">
                        {new Date(product.createdAt).toLocaleDateString("ar-KW")}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(product.id)}
                          disabled={deleteMutation.isPending}
                          className="text-destructive hover:bg-destructive/10"
                        >
                          {deleteMutation.isPending ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </main>
    </div>
  );
}
