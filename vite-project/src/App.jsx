import React from 'react';

export default function ThesisWebsite() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      <header className="max-w-4xl mx-auto py-6">
        <nav className="flex items-center justify-between">
          <h1 className="text-2xl font-extrabold">Agentic AI — Energy Defense</h1>
        </nav>
      </header>

      <main className="max-w-4xl mx-auto bg-white shadow rounded-lg p-8">
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-2">Thesis</h2>
          <p className="text-gray-700">
            In this project, we will focus on the following thesis: <strong>Agentic AI in the physical and digital protection of neighborhood
            substation transformers would decrease incident response time by 10%.</strong> Substations are critical nodes in the energy grid, yet
            they remain vulnerable to both cyberattacks and physical disruptions. By deploying AI agents capable of real-time monitoring,
            anomaly detection, and automated response coordination, utilities can strengthen defensive measures and reduce the lag between
            detection and remediation.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-2">rough outline</h2>
          <ol className="list-decimal pl-5 space-y-2 text-gray-700">
            <li><strong>Introduction & Motivation</strong> — state of substations, threat surface, and why response time matters.</li>
            <li><strong>Related Work</strong> — agentic AI, grid security, power system monitoring, co-simulation approaches.</li>
            <li><strong>Problem & Thesis</strong> — formalize the 10% response-time reduction hypothesis and defense posture.</li>
            <li><strong>Methodology</strong> — co-simulation architecture, datasets, metrics, and experimental design.</li>
            <li><strong>Simulations & Experiments</strong> — power-flow scenarios, communication/latency tests, cyber-physical attack injects.</li>
            <li><strong>Results & Analysis</strong> — performance, sensitivity, limitations.</li>
            <li><strong>Proposed Solutions</strong> — agent designs, deployment patterns, recommended operational changes.</li>
            <li><strong>Conclusions & Future Work</strong> — roadmap to real-world trials and extension beyond neighborhood substations.</li>
          </ol>
        </section>

        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-2">Planned simulations (co-simulation)</h2>
          <p className="text-gray-700 mb-3">
            We'll use a co-simulation approach to study the interplay between electrical behavior and communication/control infrastructure.
            The high-level mapping below shows components and intended roles:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded">
              <h3 className="font-semibold">Power-system modelling</h3>
              <ul className="list-disc pl-5 text-gray-700 mt-2">
                <li><strong>pandapower</strong> (Python) — model the neighborhood distribution topology, run steady-state power flow and
                  contingency analyses, place transformers/substations, and emulate faults and load variations.</li>
                <li><strong>GridLAB-D</strong> (optional/alternative) — detailed distribution system modeling (equipment-level behavior, time-series
                  simulations) and validation of pandapower scenarios.</li>
              </ul>
            </div>

            <div className="p-4 border rounded">
              <h3 className="font-semibold">Communication & control simulation</h3>
              <ul className="list-disc pl-5 text-gray-700 mt-2">
                <li><strong>EXATA</strong> — simulate the communication between grid controllers, RTUs/IEDs, and agentic AI controllers; measure
                  latency, packet loss, and how these affect anomaly detection & orchestrated responses.</li>
                <li>Model controller placements, SCADA/DER communications, and realistic network topologies (wired/radio links).</li>
              </ul>
            </div>
          </div>

          <p className="text-sm text-gray-500 mt-3">Note: pandapower and GridLAB-D are Python/C-based tools run locally or on compute nodes; EXATA is a separate network simulator — data exchange will be via files, sockets, or a co-simulation orchestrator (e.g., HELICS or custom bridge).</p>
        </section>

        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-2">Example experiments & metrics</h2>
          <ul className="list-disc pl-5 text-gray-700 space-y-2">
            <li><strong>Baseline:</strong> no agentic AI. Measure detection-to-start-of-response time across injected events (physical disturbance, fault, or simulated cyber compromise).</li>
            <li><strong>Agentic AI enabled:</strong> agents run distributed on edge/controllers; measure detection, decision, and orchestration latency. Compare response-time improvement (target: 10% reduction).</li>
            <li><strong>Network stress tests:</strong> vary latency/packet-loss in EXATA and measure downstream effects on response time and false positives/negatives.</li>
            <li><strong>Power impact:</strong> use pandapower to quantify how faster responses reduce the area/extent/duration of voltage violations, thermal overloads, and unserved load.</li>
          </ul>
        </section>
      </main>
    </div>
  );
}
