# Wolfi PHP Runtimes

PHP **8.2, 8.3, 8.4 and 8.5**, the branches [php.net supports](https://www.php.net/supported-versions.php), on Wolfi for `linux/amd64` and `linux/arm64`, with a hardened `php.ini`.

| Branch | php.net support | Image release | PHP2Shell fix |
| :--- | :--- | :--- | :--- |
| 8.5 | Active until 31 Dec 2027, security until 31 Dec 2029 | 8.5.12 | 8.5.12 |
| 8.4 | Active until 31 Dec 2026, security until 31 Dec 2028 | 8.4.27 | 8.4.27 |
| 8.3 | Security fixes only, until 31 Dec 2027 | 8.3.36 | 8.3.36 |
| 8.2 | Security fixes only, until 31 Dec 2026 | 8.2.35 | 8.2.35 |

PHP 8.1 and older are end of life and not built. The Daily Dependency Update moves each branch to Wolfi's newest release.

## Flavors

| Tag | Contents |
| :--- | :--- |
| `ghcr.io/taha2samy-3/php:8.4` | **prod**: PHP-FPM on port 9000, built from scratch with **no shell, no busybox and no package manager**, UID `1000`. The package database is kept so vulnerability scanners see every package. |
| `ghcr.io/taha2samy-3/php:8.4-dev` | **dev**: PHP CLI and PHP-FPM, Composer (verified against getcomposer.org's SHA-256), `build-base`, `git`, `unzip`, busybox and `apk`, UID `1000`. |

Both include: bcmath, ctype, curl, dom, fileinfo, gd, iconv, intl, mbstring, mysqlnd, OPcache, openssl, PDO (MySQL, PostgreSQL, SQLite), phar, session, SimpleXML, sodium, sockets, tokenizer, XML, XMLReader, XMLWriter, zip.

## PHP2Shell (CVE-2026-109618, CVE-2026-109619)

Two unauthenticated remote code execution flaws in PHP's request handling, affecting every SAPI that serves web requests (PHP-FPM, mod_php, CGI). Updating is the only complete fix; PHP fixed them in 8.5.12, 8.4.27, 8.3.36 and 8.2.35.

- Every image ships a fixed release. The prod build fails if the PHP version predates the fix.
- On top of the fix, the images apply PHP's interim guidance as defence in depth: `session.upload_progress.enabled = 0`, `fatal_error_backtraces = Off` (8.5), smaller request bodies and input nesting, FPM workers recycled with `pm.max_requests`, and the critical settings set with `php_admin_value` in the FPM pool so a front end cannot change them per request with `PHP_VALUE`.
- Restart, or redeploy, every PHP worker after updating so the fix takes effect.

## Hardening

All images (`/etc/php/conf.d/90-hardened.ini`):

- No version disclosure (`expose_php = Off`), errors logged to stderr and never displayed.
- Strict sessions: strict mode, cookie-only IDs, `HttpOnly`, `Secure`, `SameSite=Lax`.
- `allow_url_include = Off`; request limits `post_max_size = 32M`, `upload_max_filesize = 16M`, `max_file_uploads = 10`, `max_input_vars = 1000`, `max_input_nesting_level = 32`.

prod only (`95-prod.ini` and the FPM pool):

- `disable_functions = exec, passthru, shell_exec, system, proc_open, popen, pcntl_exec`.
- `allow_url_fopen = Off` (use the curl extension for HTTP).
- OPcache with `validate_timestamps = 0`, since the code is baked into the image.
- FPM: runs only `.php` files, logs to stderr, keeps the container environment (`clear_env = no`), and answers `/fpm-ping` and `/fpm-status` over FastCGI.

An application can relax a setting with its own file, for example `COPY my.ini /etc/php/conf.d/99-app.ini`. The `php_admin_value` settings in the FPM pool can only be changed by replacing `/etc/php/php-fpm.d/www.conf`.

## Usage

```dockerfile
FROM ghcr.io/taha2samy-3/php:8.4-dev AS build
COPY --chown=1000:1000 . /app
RUN composer install --no-dev --classmap-authoritative --no-interaction

FROM ghcr.io/taha2samy-3/php:8.4
COPY --from=build --chown=1000:1000 /app /app
```

Put a web server such as nginx in front and forward PHP requests over FastCGI:

```nginx
location ~ \.php$ {
    fastcgi_pass php:9000;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME /app/public$fastcgi_script_name;
}
```

Do not forward `PHP_VALUE` or `PHP_ADMIN_VALUE` from the web server.

## Build-time checks

The prod build runs `conf/verify-prod.php` as the runtime user and fails if a hardening setting, a disabled function, the PHP2Shell fix level or an extension is missing, then runs `php-fpm --test`. The dev build fails if any extension prints a startup warning.
