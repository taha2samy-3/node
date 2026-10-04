import { ExternalLink } from 'lucide-react';
import { Card, Command, Stagger, StaggerItem } from '../../components/ui';
import { ATTESTATIONS_URL, OWNER, REPO_URL, packageUrl, type Flavor } from '../../lib/catalog';
import { getImageMeta } from '../../lib/reports';

export default function ProvenanceTab({ flavor }: { flavor: Flavor }) {
  const tag = flavor.tags[0];
  const { digest } = getImageMeta(tag);

  const checks = [
    {
      title: 'Verify the build provenance',
      text: 'Checks the SLSA provenance signed by GitHub Actions for this image against the workflow in this repository.',
      command: `gh attestation verify oci://${tag} --owner ${OWNER}`,
    },
    {
      title: 'Verify the SBOM attestation',
      text: 'Checks the signed CycloneDX SBOM attached to the image.',
      command: `gh attestation verify oci://${tag} --owner ${OWNER} --predicate-type https://cyclonedx.org/bom`,
    },
    {
      title: 'Download the attestations',
      text: 'Saves the signed Sigstore bundles as JSON for offline review.',
      command: `gh attestation download oci://${tag} --owner ${OWNER}`,
    },
  ];

  const links = [
    { label: 'Attestations in this repository', href: ATTESTATIONS_URL },
    { label: 'Container package', href: packageUrl(tag) },
    { label: 'Build workflow', href: `${REPO_URL}/actions/workflows/build.yml` },
    ...(digest ? [{ label: 'Sigstore transparency log', href: `https://search.sigstore.dev/?hash=${digest.replace('sha256:', '')}` }] : []),
  ];

  return (
    <div className="space-y-6">
      <p className="max-w-3xl text-sm leading-relaxed text-slate-600 dark:text-slate-400">
        After each build, GitHub Actions attaches two signed attestations to the image: SLSA build provenance and a CycloneDX SBOM.
        They are signed with the workflow's OIDC identity through Sigstore, so anyone can verify where and how the image was built.
      </p>

      <Stagger className="space-y-4">
        {checks.map((check) => (
          <StaggerItem key={check.title}>
            <Card className="space-y-3 p-5">
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">{check.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{check.text}</p>
              </div>
              <Command command={check.command} />
            </Card>
          </StaggerItem>
        ))}
      </Stagger>

      <div className="flex flex-wrap gap-2">
        {links.map((link) => (
          <a
            key={link.label}
            href={link.href}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:border-emerald-500 hover:text-emerald-700 dark:border-slate-700 dark:text-slate-300 dark:hover:border-brand-mint dark:hover:text-brand-mint"
          >
            {link.label} <ExternalLink className="h-3.5 w-3.5" />
          </a>
        ))}
      </div>
    </div>
  );
}
