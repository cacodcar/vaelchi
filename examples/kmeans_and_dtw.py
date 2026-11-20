"""OpenAI Codex: representative periods and independent sequence alignment."""

import json

from vaelchi import dtw, kmeans


def main():
    """Print portable clustering and alignment results for two small cases."""
    clustered = kmeans(
        [0, 1, 10, 11, 0, 1, 10, 11],
        periods=2,
        period_length=2,
    )
    aligned = dtw([0, 10], [10])
    print(
        json.dumps(
            {
                "clustering": clustered.to_dict(),
                "alignment": aligned.to_dict(),
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
