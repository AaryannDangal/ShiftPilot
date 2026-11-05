import "@/styles/globals.css";
import { Providers } from "./providers";

export const metadata = {
  title: "ShiftPilot",
  description: "Intelligent workforce scheduling platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
