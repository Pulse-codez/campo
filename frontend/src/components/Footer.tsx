export default function Footer() {
  return (
    <footer className="border-t border-[rgba(238,243,255,0.12)] bg-[rgb(1,3,10)] mt-auto">
      <div className="container px-4 py-10">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-[rgba(238,243,255,0.62)]">
            Campus Support Companion — peer-style support for university students in Kenya.
          </div>
          <div className="flex gap-4 text-sm">
            <a href="/privacy" className="text-[rgba(238,243,255,0.7)] hover:text-white transition-colors">
              Privacy
            </a>
            <a href="/terms" className="text-[rgba(238,243,255,0.7)] hover:text-white transition-colors">
              Terms
            </a>
            <a href="/accessibility" className="text-[rgba(238,243,255,0.7)] hover:text-white transition-colors">
              Accessibility
            </a>
          </div>
        </div>
        <div className="mt-8 pt-6 border-t border-[rgba(238,243,255,0.12)] text-xs text-[rgba(238,243,255,0.5)]">
          Not an emergency service. If you or someone else is in immediate danger,
          call <strong className="text-white">1199</strong> (national mental health helpline, 24/7, free) or go to the nearest
          hospital emergency department.
        </div>
      </div>
    </footer>
  );
}
