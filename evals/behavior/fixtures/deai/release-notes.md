# Release notes: telemetry-ingest 2.4.0

In today's rapidly evolving landscape of observability, telemetry-ingest 2.4.0 represents a
pivotal milestone in our journey toward seamless, scalable data ingestion. This release is
not just an update—it is a fundamental reimagining of how we think about telemetry.

## Key highlights

At its core, this release delivers a robust, comprehensive, and battle-tested set of
improvements that empower teams to unlock the full potential of their observability
strategy. It is important to note that these changes were designed with flexibility,
scalability, and reliability in mind.

- **Enhanced performance.** We've significantly improved throughput. In our testing, ingest
  throughput increased from 41K events/s to 63K events/s on a single `ingest-worker` pod.
- **Streamlined configuration.** The `--batch-size` flag now accepts values up to `10000`.
  The default remains `500`.
- **Improved reliability.** Retries now use exponential backoff starting at `250ms` and
  capping at `30s`.

## Upgrade notes

If you are running `2.3.x`, upgrade by setting the image tag to `ghcr.io/acme/telemetry-ingest:2.4.0`.
Note that the `TELEMETRY_INGEST_LEGACY_MODE` environment variable has been removed. Set it
to any value and the process will now exit with code `2` and print
`fatal: TELEMETRY_INGEST_LEGACY_MODE is no longer supported`.

Run the following to verify the upgrade:

```bash
telemetry-ingest --version
# expected: telemetry-ingest 2.4.0
```

## Looking ahead

As we look to the future, we remain committed to pushing the boundaries of what's possible.
This release is a testament to our unwavering dedication to excellence, and we can't wait to
see what you build with it. In conclusion, telemetry-ingest 2.4.0 is a game-changer that will
transform the way your organization approaches observability.