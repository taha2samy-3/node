<?php
// Build-time check of the prod image, run as the runtime user. Deletes itself when it passes.
$fail = static function (string $message): never {
    fwrite(STDERR, "verify-prod: $message\n");
    exit(1);
};

// An extension that failed to load leaves a startup warning behind
if (($error = error_get_last()) !== null) {
    $fail('startup: ' . $error['message']);
}

$expected = [
    'session.upload_progress.enabled' => '0', // PHP2Shell CVE-2026-109619 path
    'expose_php' => '',
    'allow_url_fopen' => '',
    'display_errors' => '',
    'opcache.validate_timestamps' => '0',
];
if (PHP_VERSION_ID >= 80500) {
    $expected['fatal_error_backtraces'] = ''; // PHP2Shell CVE-2026-109619 path, 8.5 only
}
foreach ($expected as $key => $value) {
    $actual = ini_get($key);
    if ($actual === false || (string) $actual !== $value) {
        $fail("$key is " . var_export($actual, true) . ", expected " . var_export($value, true));
    }
}

foreach (['shell_exec', 'exec', 'system', 'proc_open'] as $function) {
    if (function_exists($function) && is_callable($function)) {
        $fail("$function is not disabled");
    }
}

// Releases that contain the PHP2Shell fixes (CVE-2026-109618, CVE-2026-109619)
$fixed = ['8.2' => '8.2.35', '8.3' => '8.3.36', '8.4' => '8.4.27', '8.5' => '8.5.12'];
$branch = PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION;
if (!isset($fixed[$branch]) || version_compare(PHP_VERSION, $fixed[$branch], '<')) {
    $fail(PHP_VERSION . ' predates the PHP2Shell fix for ' . $branch);
}

echo 'PHP ', PHP_VERSION, " prod hardening verified\n";
unlink(__FILE__);
