import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys


def csv_to_heatmap(input_csv, output_png):
    """
    Converts a CSV file with axis labels into a heatmap and saves it as a PNG.

    Args:
        input_csv (str): Path to the input CSV file.
        output_png (str): Path to save the output PNG file.
    """
    # Read the CSV into a pandas DataFrame
    df = pd.read_csv(input_csv, index_col=0)

    # Since the values in the original dataframe are not appropriate for a heatmap,
    # we normalize them to be between 0 and 1
    df_normalized = (df - df.values.min()) / (df.values.max() - df.values.min())

    plt.figure(figsize=(12, 8))

    sns.heatmap(df_normalized,
                cmap='viridis',
                annot=True,
                fmt='.2f',
                cbar=True,
                square=True,
                annot_kws={'size': 8},
                linewidths=0.5)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python heatmap.py <input_csv> <output_png>")
        sys.exit(1)

    csv_to_heatmap(sys.argv[1], sys.argv[2])
