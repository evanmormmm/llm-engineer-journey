from collections.abc import Mapping


def merge_configs(
    base: Mapping[str, object],
    override: Mapping[str, object],
) -> dict[str, object]:
    result = dict(base)
    result.update(override)
    return result


def split_batches[T](
    items: list[T],
    batch_size: int,
) -> list[list[T]]:
    batches: list[list[T]] = []

    for i in range(0, len(items), batch_size):
        batches.append(items[i : i + batch_size])

    return batches


def find_best(
    candidates: list[tuple[str, float]],
) -> str | None:
    if not candidates:
        return None

    return max(candidates, key=lambda candidate: candidate[1])[0]
