# Cache Metrics Guide

## What to Measure

Track these metrics to evaluate cache effectiveness:

- **prompt_cache_hit_tokens** -- tokens served from the provider's prompt cache.
  Higher is better. This is the tokens the provider did not need to re-process.
- **prompt_cache_miss_tokens** -- tokens not in cache and processed fresh.
  Lower is better. Spikes here indicate stable content was modified or ordering
  changed between calls.
- **cached_tokens** -- total tokens in the cached prefix portion of the prompt.
  This is the theoretical maximum; actual hit rate depends on prefix stability.
- **latency** -- time-to-first-token for the API response. Cached prompts
  typically show 30-50% latency reduction compared to uncached.
- **cost** -- dollar cost per API call. Cached tokens are billed at a reduced
  rate by most providers (often 50% of the input token price).

## Using harness cache-report

Run the CLI command to get a snapshot of cache performance:

```bash
harness cache-report
```

Example output:

```
Cache Report
Stable prefix:   8,420 tokens (hash: a3f2c1)
Semi-stable:     2,130 tokens (hash: 7b4e9d)
Feature context: 4,800 tokens (hash: 1c5f8a)
Dynamic suffix:  1,200 tokens

Estimated total:  16,550 tokens
Cacheable prefix: 15,350 tokens (92.8%)

Last 20 API calls (if metrics available):
  avg cached tokens:   9,600
  avg miss tokens:     3,100
  estimated hit ratio: 75.6%
  avg latency:         1.8s (vs 3.2s uncached baseline)
```

### Interpreting the report

- **Cacheable prefix percentage**: should be above 80%. If below, check that
  dynamic content has not leaked into the stable layers.
- **Hash stability**: if stable_prefix hash changes between reports, something
  in the stable layer was modified unexpectedly.
- **Hit ratio**: 70%+ is good. Below 50% means the prefix is not stable enough
  or ordering is inconsistent between calls.

## Provider-Specific Notes

- **Anthropic (Claude)**: Prompt caching is automatic for repeated prefixes.
  Cached tokens are billed at 10% of the base input price. Cache TTL is 5
  minutes with no minimum token requirement.
- **OpenAI (GPT-4o)**: Automatic prompt caching with a 256-token minimum prefix
  length. Cached tokens billed at 50% of input price. Cache TTL is 5-10
  minutes depending on load.
- **DeepSeek (V3/R1)**: Supports prefix caching. Cached tokens billed at 90%
  discount. Cache behavior depends on the API endpoint and model version.

## Agent-Only Benefits

Even when API-level cache metrics are not available (no access to provider
dashboards or response headers), stable context ordering provides measurable
benefits:

- **Fewer re-reads.** The agent sees stable content in its context and does not
  waste a tool call reading the same policy file it already has.
- **Consistent behavior.** Deterministic ordering means the agent makes the same
  decisions given the same feature, reducing non-deterministic output.
- **Lower truncation risk.** When context windows fill up during long sessions,
  stable content at the top is more likely to survive than content scattered
  randomly throughout the prompt.
- **Easier debugging.** If behavior changes, check whether a stable layer hash
  changed. This narrows the root cause immediately.
