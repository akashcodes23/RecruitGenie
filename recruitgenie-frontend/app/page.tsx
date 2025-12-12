export default function Home() {
  return (
    <main style={{ padding: 40, fontFamily: 'Inter, system-ui, sans-serif' }}>
      <h1>RecruitGenie</h1>
      <p>AI-driven candidate screening — frontend connected to backend.</p>
      <ul>
        <li><a href="/upload">Upload resume</a></li>
        <li><a href="/candidates">Candidates</a></li>
        <li><a href="/analytics">Analytics</a></li>
      </ul>
    </main>
  );
}