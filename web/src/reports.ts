const allReports = import.meta.glob('../../reports/*.json', { eager: true });

export const configData: Record<string, any> =
  (allReports['../../reports/config.json'] as any)?.default ||
  allReports['../../reports/config.json'] ||
  {};

export const reportsMap: Record<string, Record<string, Record<string, any>>> = {};

const fallbackKeys: [string, string, string, any][] = [];

Object.entries(allReports).forEach(([path, data]) => {
  const match = path.match(/\/reports\/(.+?)-(dev|prod|standard)-(vuln|cis|sbom)\.json$/);
  if (match) {
    const [, verKey, flavor, type] = match;
    const reportData = (data as any).default || data;

    // Exact key, e.g. "openjdk-21", "node-fips-22" or "22"
    if (!reportsMap[verKey]) reportsMap[verKey] = {};
    if (!reportsMap[verKey][flavor]) reportsMap[verKey][flavor] = {};
    reportsMap[verKey][flavor][type] = reportData;

    // Bare version alias ("21" for "openjdk-21"), applied after all exact keys
    if (verKey.includes('-')) {
      fallbackKeys.push([verKey.split('-').pop()!, flavor, type, reportData]);
    }
  }
});

// Aliases only fill gaps: "openjdk-21" must never replace the reports of java:21
fallbackKeys.forEach(([key, flavor, type, reportData]) => {
  if (!reportsMap[key]) reportsMap[key] = {};
  if (!reportsMap[key][flavor]) reportsMap[key][flavor] = {};
  if (!reportsMap[key][flavor][type]) reportsMap[key][flavor][type] = reportData;
});
