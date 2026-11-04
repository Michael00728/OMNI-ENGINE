const capabilities = [
  { title: "Regulatory intelligence", detail: "Version-aware source research with authority classification and citation provenance." },
  { title: "Credit evidence", detail: "A foundation for structured report ingestion, reconciliation, and explainable findings." },
  { title: "Financial readiness", detail: "Scenario planning for utilization, debt management, and lending preparation." },
];

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar"><span className="brand">OMNI-ENGINE</span><span className="status">FOUNDATION / 0.1.0</span></header>
      <section className="hero">
        <p className="eyebrow">ENTERPRISE CREDIT INTELLIGENCE</p>
        <h1>Evidence first.<br /><span>Clarity at every step.</span></h1>
        <p className="intro">A structured platform for credit intelligence, regulatory research, dispute evidence, and financial readiness.</p>
      </section>
      <section className="grid" aria-label="Platform capabilities">
        {capabilities.map((item, index) => (
          <article className="panel" key={item.title}>
            <span className="number">0{index + 1}</span>
            <h2>{item.title}</h2>
            <p>{item.detail}</p>
          </article>
        ))}
      </section>
      <footer>FOUNDATION BUILD · Automated analysis is informational and subject to evidence validation and human review.</footer>
    </main>
  );
}
