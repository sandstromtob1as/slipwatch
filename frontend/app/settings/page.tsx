export default function Settings() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-24">
      <div className="mx-auto max-w-3xl rounded-3xl border border-gray-700 bg-slate-950/90 p-12 text-center shadow-xl shadow-black/30">
        <h1 className="text-4xl font-bold text-white mb-4">Settings</h1>
        <p className="text-gray-300 text-lg mb-6">
          The settings page is temporarily disabled. It will return in a later update.
        </p>
        <div className="inline-flex items-center gap-3 rounded-full bg-gray-800 px-5 py-3 text-sm text-gray-400">
          <span className="h-2 w-2 rounded-full bg-blue-400" />
          Use the Overview or Alert Log pages for now.
        </div>
      </div>
    </div>
  );
}
