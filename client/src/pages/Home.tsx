import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { trpc } from "@/lib/trpc";
import { Phone, MessageCircle, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const { data: products = [], isLoading } = trpc.products.list.useQuery();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? "bg-background/95 backdrop-blur shadow-lg" : "bg-transparent"
        }`}
      >
        <div className="container flex items-center justify-between h-20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
              <span className="text-primary-foreground font-bold">س</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-primary">سالفورد</h1>
              <p className="text-sm text-muted-foreground">للأثاث والمفروشات</p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8">
            <a href="#products" className="hover:text-primary transition-colors">
              المنتجات
            </a>
            <a href="#about" className="hover:text-primary transition-colors">
              عن الشركة
            </a>
            {isAuthenticated && user?.role === "admin" && (
              <a href="/dashboard" className="hover:text-primary transition-colors">
                لوحة التحكم
              </a>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 bg-gradient-to-b from-primary/5 to-background">
        <div className="container">
          <div className="max-w-2xl mx-auto text-center space-y-6">
            <h2 className="text-5xl md:text-6xl font-bold leading-tight">
              أكبر تشكيلة من{" "}
              <span className="text-primary">السجاد والموكيت</span>
            </h2>
            <p className="text-xl text-muted-foreground">
              نقدم أفضل أنواع السجاد الفاخر والموكيت الحديث لجميع أنحاء الكويت
            </p>
            <div className="flex gap-4 justify-center pt-4">
              <Button
                size="lg"
                className="bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                تصفح المنتجات
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-primary text-primary hover:bg-primary/10"
              >
                تواصل معنا
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section id="products" className="py-20">
        <div className="container">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold mb-4">منتجاتنا المميزة</h3>
            <p className="text-muted-foreground text-lg">
              تصفح مجموعتنا الواسعة من السجاد والموكيت الفاخر
            </p>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-muted-foreground text-lg">
                لا توجد منتجات متاحة حالياً
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product) => (
                <Card
                  key={product.id}
                  className="overflow-hidden hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer group"
                >
                  {product.imageUrl && (
                    <div className="relative w-full h-64 overflow-hidden bg-muted">
                      <img
                        src={product.imageUrl}
                        alt={product.title}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                      />
                    </div>
                  )}
                  <div className="p-6">
                    <h4 className="text-xl font-bold mb-2">{product.title}</h4>
                    {product.description && (
                      <p className="text-muted-foreground line-clamp-2">
                        {product.description}
                      </p>
                    )}
                    <div className="mt-4 pt-4 border-t border-border">
                      <Button
                        variant="outline"
                        className="w-full border-primary text-primary hover:bg-primary/10"
                      >
                        استفسر الآن
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-primary/5">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <h3 className="text-4xl font-bold">عن سالفورد</h3>
            <p className="text-lg text-muted-foreground leading-relaxed">
              شركة سالفورد متخصصة في توفير أفضل أنواع السجاد والموكيت الفاخر في الكويت.
              نقدم خدمة عملاء متميزة وتصاميم حديثة تناسب جميع الأذواق والميزانيات.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-8">
              <div className="space-y-2">
                <div className="text-3xl font-bold text-primary">+500</div>
                <p className="text-muted-foreground">منتج متنوع</p>
              </div>
              <div className="space-y-2">
                <div className="text-3xl font-bold text-primary">+1000</div>
                <p className="text-muted-foreground">عميل راضٍ</p>
              </div>
              <div className="space-y-2">
                <div className="text-3xl font-bold text-primary">24/7</div>
                <p className="text-muted-foreground">خدمة العملاء</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Floating Contact Buttons */}
      <div className="fixed bottom-8 right-8 flex flex-col gap-4 z-40">
        <a
          href="https://wa.me/96555943343"
          target="_blank"
          rel="noopener noreferrer"
          className="w-14 h-14 bg-green-500 hover:bg-green-600 text-white rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110"
          title="واتساب"
        >
          <MessageCircle className="w-6 h-6" />
        </a>
        <a
          href="tel:+96555943343"
          className="w-14 h-14 bg-primary hover:bg-primary/90 text-primary-foreground rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110"
          title="اتصال"
        >
          <Phone className="w-6 h-6" />
        </a>
      </div>

      {/* Footer */}
      <footer className="bg-primary/10 border-t border-border py-12">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h4 className="font-bold mb-4">سالفورد</h4>
              <p className="text-muted-foreground">
                متخصصون في السجاد والموكيت الفاخر بأفضل الأسعار
              </p>
            </div>
            <div>
              <h4 className="font-bold mb-4">روابط سريعة</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <a href="#products" className="hover:text-primary transition-colors">
                    المنتجات
                  </a>
                </li>
                <li>
                  <a href="#about" className="hover:text-primary transition-colors">
                    عن الشركة
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">تواصل معنا</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <a
                    href="tel:+96555943343"
                    className="hover:text-primary transition-colors"
                  >
                    +965 55943343
                  </a>
                </li>
                <li>
                  <a
                    href="https://wa.me/96555943343"
                    className="hover:text-primary transition-colors"
                  >
                    واتساب
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border pt-8 text-center text-muted-foreground">
            <p>&copy; 2026 سالفورد للأثاث والمفروشات. جميع الحقوق محفوظة.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
