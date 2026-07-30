const allReports = import.meta.glob('../../reports/*.json', { eager: true });

export const reportsMap: Record<string, Record<string, Record<string, any>>> = {};

Object.entries(allReports).forEach(([path, data]) => {
  const match = path.match(/\/reports\/(.+?)-(dev|prod)-(vuln|cis|sbom)\.json$/);
  if (match) {
    const [, version, flavor, type] = match;
    if (!reportsMap[version]) reportsMap[version] = {};
    if (!reportsMap[version][flavor]) reportsMap[version][flavor] = {};
    reportsMap[version][flavor][type] = (data as any).default || data;
  }
});