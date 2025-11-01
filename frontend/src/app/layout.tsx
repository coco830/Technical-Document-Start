import { Inter } from "next/font/google"
import { Metadata } from "next"
import "@/styles/globals.css"
import { ThemeProvider } from "@/components/theme"
import { ToastProviderWithContainer } from "@/components/ui/toast"
import { ErrorBoundary } from "@/components/state"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: {
    default: "悦恩人机共写平台",
    template: "%s | 悦恩人机共写平台"
  },
  description: "一个创新的人机协作写作平台，让AI与人类共同创作优秀内容",
  keywords: ["AI写作", "人机协作", "内容创作", "写作平台"],
  authors: [{ name: "悦恩团队" }],
  creator: "悦恩团队",
  publisher: "悦恩团队",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"
  ),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "zh_CN",
    url: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
    title: "悦恩人机共写平台",
    description: "一个创新的人机协作写作平台，让AI与人类共同创作优秀内容",
    siteName: "悦恩人机共写平台",
    images: [
      {
        url: "/images/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "悦恩人机共写平台",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "悦恩人机共写平台",
    description: "一个创新的人机协作写作平台，让AI与人类共同创作优秀内容",
    images: ["/images/og-image.jpg"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
  other: {
    "msapplication-TileColor": "#000000",
    "msapplication-config": "/browserconfig.xml",
  },
}

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={inter.className}>
        <ErrorBoundary variant="default">
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem={true}
            storageKey="yueen-theme"
          >
            <ToastProviderWithContainer>
              {children}
            </ToastProviderWithContainer>
          </ThemeProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
