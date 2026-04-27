# Проверка runtime/gradient duration как возможных proxy-признаков RT

Мини-исследование проверяет, ведут ли себя `gradient_duration_min` и `total_runtime_min` как честные параметры LC-метода или как proxy-признаки, частично следующие из ожидаемого/измеренного RT. Для всех вариантов используется одна и та же подвыборка, один и тот же grouped split по соединениям и одна ExtraTrees-модель.

## Сравнение ablation-режимов

| ablation | n_train | n_test | n_features | uses_gradient_duration_min | uses_total_runtime_min | mae | rmse | r2 | spearman | normalized_mae_runtime_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| with_both | 16215 | 3785 | 73 | True | True | 1.6136 | 2.6176 | 0.9189 | 0.9368 | 6.0753 |
| without_total_runtime | 16215 | 3785 | 72 | True | False | 1.618 | 2.6103 | 0.9193 | 0.936 | 6.0918 |
| without_gradient_duration | 16215 | 3785 | 72 | False | True | 1.6231 | 2.6473 | 0.917 | 0.935 | 6.1111 |
| without_both | 16215 | 3785 | 71 | False | False | 1.6566 | 2.9183 | 0.8992 | 0.9348 | 6.237 |

## Диагностика “runtime как следствие RT”

- Строк в подвыборке: 20000
- Split group column: `inchikey`
- Пересечение compound-групп train/test: 0
- Spearman(`rt_min`, `total_runtime_min`): 0.478
- Spearman(`rt_min`, `gradient_duration_min`): 0.601
- Медианный запас после пика (`total_runtime_min - rt_min`): 11.500 мин
- Q10/Q90 запаса после пика: 2.660 / 29.261 мин
- Медиана `rt_min / total_runtime_min`: 0.484
- Доля строк, где метод заканчивается через 0-2 мин после RT: 0.056
- Проверено method-групп: 139
- Доля method-групп, где runtime меняется внутри одного method key: 0.036

## Интерпретация

На этой публичной подвыборке нет сильного простого сигнала, что `total_runtime_min` является следствием RT: корреляция умеренная, медианный запас после пика большой, а внутри одинаковых method-групп runtime почти не меняется. Но ablation всё равно нужно регулярно показывать, потому что во внутренних targeted bioanalytical assays runtime действительно может задаваться после знания ожидаемого пика.

## Как понять, является ли runtime следствием

1. Если `total_runtime_min` меняется от аналита к аналиту внутри одной method-family и монотонно следует за `rt_min`, это похоже на operational choice, выбранный под ожидаемый пик.
2. Если `total_runtime_min - rt_min` мал и стабилен, runtime может кодировать правило “остановить метод вскоре после целевого пика”.
3. Если `total_runtime_min` одинаков для многих соединений в одном методе, это скорее независимый параметр метода, а не следствие конкретного RT.
4. Если удаление `total_runtime_min` резко ухудшает метрики, а удаление химических/method composition признаков нет, модель, вероятно, использует runtime как shortcut.
5. Самая сильная проверка для внутренних данных: сравнить дизайн метода до запуска с наблюдаемым RT после запуска. Параметр, выбранный после знания RT, нельзя использовать как causal predictor.

## Рекомендация

`full_method` можно использовать как практический operational predictor. Для научных выводов, transfer-валидации и inverse recommendation нужно отдельно показывать `no_runtime_proxy` benchmark, а runtime трактовать в основном как constraint/penalty, а не как свободный predictive feature.
