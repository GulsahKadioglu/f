import { AppProps } from 'next/app';
import "../styles/globals.css";
import { AuthProvider } from '../src/context/AuthContext';
import Link from 'next/link';
import { ThemeProvider as NextThemesProvider } from 'next-themes';
import ThemeSwitcher from "../src/components/ThemeSwitcher";

function MyApp({ Component, pageProps }: AppProps) {
  const AnyNextThemesProvider = NextThemesProvider as any;
  return (
    <div className={`bg-white text-black dark:bg-gray-900 dark:text-white transition-colors duration-300`}>
      <AnyNextThemesProvider attribute="class" defaultTheme="system" enableSystem>
        <AuthProvider>
          <header className="p-4 flex justify-end">
            <Link href="/dashboard" className="mr-4 px-4 py-2 rounded-md bg-blue-500 text-white hover:bg-blue-600 dark:bg-gray-700 dark:hover:bg-gray-600">
              Dashboard
            </Link>
            <ThemeSwitcher />
          </header>
          <Component {...pageProps} />
        </AuthProvider>
      </AnyNextThemesProvider>
    </div>
  );
}

export default MyApp;
