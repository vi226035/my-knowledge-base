document$.subscribe(function() {
  mermaid.initialize({
    startOnLoad: false,
    theme: document.documentElement.getAttribute("data-md-color-scheme") === "slate" ? "dark" : "default",
    securityLevel: "loose",
    flowchart: { useMaxWidth: true, htmlLabels: true },
    sequence: { useMaxWidth: true, wrap: true }
  });
  mermaid.run({
    querySelector: ".mermaid"
  });
});
