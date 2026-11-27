export default function Footer() {
  return (
    <footer className="border-t border-[rgb(229,231,235)] bg-white mt-auto">
      <div className="container px-4 py-10">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-[rgb(107,114,128)]">
            Campus Support Companion — peer-style support for university students in Kenya.
          </div>
          <div className="flex gap-4 text-sm">
            <a href="/privacy" className="text-[rgb(107,114,128)] hover:text-[rgb(20,137,103)]">
              Privacy
            </a>
            <a href="/terms" className="text-[rgb(107,114,128)] hover:text-[rgb(20,137,103)]">
              Terms
            </a>
            <a href="/accessibility" className="text-[rgb(107,114,128)] hover:text-[rgb(20,137,103)]">
              Accessibility
            </a>
          </div>
        </div>
        <div className="mt-8 pt-6 border-t border-[rgb(229,231,235)] text-xs text-[rgb(107,114,128)]">
          Not an emergency service. If you or someone else is in immediate danger,
          call <strong>1199</strong> (national mental health helpline, 24/7, free) or go to the nearest
          hospital emergency department.
        </div>
      </div>
    </footer>
  );
}
