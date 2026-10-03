const allReports = import.meta.glob('../../reports/*.json', { eager: true });

export const configData: Record<string, any> = 
  (allReports['../../reports/config.json'] as any)?.default || 
  allReports['../../reports/config.json'] || 
  {};

export const reportsMap: Record<string, Record<string, Record<string, any>>> = {};

Object.entries(allReports).forEach(([path, data]) => {
  const match = path.match(/\/reports\/(.+?)-(dev|prod|standard)-(vuln|cis|sbom)\.json$/);
  if (match) {
    const [, verKey, flavor, type] = match;
    const reportData = (data as any).default || data;
    
    // Add under original key (e.g., "openssl-3.5" or "26")
    const keys = [verKey];
    if (verKey.includes('-')) {
      const suffix = verKey.split('-').pop()!;
      keys.push(suffix);
    }
    
    keys.forEach(k => {
      if (!reportsMap[k]) reportsMap[k] = {};
      if (!reportsMap[k][flavor]) reportsMap[k][flavor] = {};
      reportsMap[k][flavor][type] = reportData;
    });
  }
});