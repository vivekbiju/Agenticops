import './globals.css';

export const metadata = {
  title: 'AgenticOps Control Center',
  description: 'Enterprise Multi-Agent Stream Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}