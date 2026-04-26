# Peak Metric Target Readiness

This report separates measured labels from provisional or derived proxy targets.

| Target | Available rows | Coverage | Label source | Readiness | Action |
| --- | ---: | ---: | --- | --- | --- |
| rt_min | 213941 | 1.000 | measured | trainable | train supervised baseline |
| quality_score | 213941 | 1.000 | derived_proxy | trainable | train supervised baseline |
| asymmetry | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| tailing_factor | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| peak_width_base_min | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| peak_width_half_height_min | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| resolution | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| sn_ratio | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| peak_area | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| peak_height | 0 | 0.000 | unavailable | unavailable | skip; collect internal lab labels |
| low_intensity_risk | 0 | 0.000 | derived_proxy | proxy_only | derive transparent risk proxy; do not claim measured peak label |
| poor_resolution_risk | 0 | 0.000 | derived_proxy | proxy_only | derive transparent risk proxy; do not claim measured peak label |
| asymmetry_risk | 0 | 0.000 | derived_proxy | proxy_only | derive transparent risk proxy; do not claim measured peak label |
| broad_peak_risk | 0 | 0.000 | derived_proxy | proxy_only | derive transparent risk proxy; do not claim measured peak label |
| void_or_unretained_risk | 0 | 0.000 | derived_proxy | proxy_only | derive transparent risk proxy; do not claim measured peak label |
| late_elution_risk | 0 | 0.000 | derived_proxy | proxy_only | derive transparent risk proxy; do not claim measured peak label |

## Interpretation

- `rt_min` is the primary supervised target.
- Public RT datasets usually lack measured asymmetry, width, resolution, S/N, and intensity labels.
- Derived risk targets are useful for MVP ranking but must be shown as provisional until internal lab outcomes are available.
