import csv
import matplotlib.pyplot as plt

def load_summary(filename="results/summary.csv"):
    rows = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def prepare_data(rows):
    # Sort configs by migration_prob
    configs = sorted(
        list(set((r["config"], float(r["migration_prob"])) for r in rows)),
        key=lambda x: x[1]
    )
    config_names = [c[0] for c in configs]
    migration_probs = [c[1] for c in configs]

    fixed_lats = []
    adaptive_lats = []
    fixed_oh = []
    adaptive_oh = []

    for cfg in config_names:
        for r in rows:
            if r["config"] == cfg and r["policy"] == "fixed_strong":
                fixed_lats.append(float(r["avg_latency"]))
                fixed_oh.append(float(r["avg_overhead"]))
            elif r["config"] == cfg and r["policy"] == "adaptive":
                adaptive_lats.append(float(r["avg_latency"]))
                adaptive_oh.append(float(r["avg_overhead"]))

    return config_names, migration_probs, fixed_lats, adaptive_lats, fixed_oh, adaptive_oh

def plot_latency_bar(config_names, fixed_lats, adaptive_lats):
    x = range(len(config_names))
    width = 0.35

    plt.figure(figsize=(6, 4))
    plt.bar([i - width/2 for i in x], fixed_lats, width, label="Fixed Strong")
    plt.bar([i + width/2 for i in x], adaptive_lats, width, label="Adaptive")

    plt.xticks(x, config_names)
    plt.xlabel("Configuration (migration rate)")
    plt.ylabel("Average Latency")
    plt.title("Average Latency: Fixed Strong vs Adaptive")
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/latency_comparison_bar.png")
    plt.show()

def plot_overhead_bar(config_names, fixed_oh, adaptive_oh):
    x = range(len(config_names))
    width = 0.35

    plt.figure(figsize=(6, 4))
    plt.bar([i - width/2 for i in x], fixed_oh, width, label="Fixed Strong")
    plt.bar([i + width/2 for i in x], adaptive_oh, width, label="Adaptive")

    plt.xticks(x, config_names)
    plt.xlabel("Configuration (migration rate)")
    plt.ylabel("Average Overhead")
    plt.title("Average Overhead: Fixed Strong vs Adaptive")
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/overhead_comparison_bar.png")
    plt.show()

def plot_latency_line(migration_probs, fixed_lats, adaptive_lats):
    plt.figure(figsize=(6, 4))
    plt.plot(migration_probs, fixed_lats, marker='o', label="Fixed Strong")
    plt.plot(migration_probs, adaptive_lats, marker='s', label="Adaptive")

    plt.xlabel("Migration Probability")
    plt.ylabel("Average Latency")
    plt.title("Average Latency vs Migration Probability")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig("results/latency_vs_migration.png")
    plt.show()

def plot_overhead_line(migration_probs, fixed_oh, adaptive_oh):
    plt.figure(figsize=(6, 4))
    plt.plot(migration_probs, fixed_oh, marker='o', label="Fixed Strong")
    plt.plot(migration_probs, adaptive_oh, marker='s', label="Adaptive")

    plt.xlabel("Migration Probability")
    plt.ylabel("Average Overhead")
    plt.title("Average Overhead vs Migration Probability")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig("results/overhead_vs_migration.png")
    plt.show()

def plot_percentage_improvement(config_names, fixed_lats, adaptive_lats, fixed_oh, adaptive_oh):
    lat_improvement = []
    oh_improvement = []

    for fl, al, fo, ao in zip(fixed_lats, adaptive_lats, fixed_oh, adaptive_oh):
        lat_imp = (fl - al) / fl * 100 if fl > 0 else 0
        oh_imp = (fo - ao) / fo * 100 if fo > 0 else 0
        lat_improvement.append(lat_imp)
        oh_improvement.append(oh_imp)

    x = range(len(config_names))
    width = 0.35

    plt.figure(figsize=(6, 4))
    plt.bar([i - width/2 for i in x], lat_improvement, width, label="Latency Improvement (%)")
    plt.bar([i + width/2 for i in x], oh_improvement, width, label="Overhead Improvement (%)")

    plt.xticks(x, config_names)
    plt.xlabel("Configuration (migration rate)")
    plt.ylabel("Improvement (%)")
    plt.title("Percentage Improvement of Adaptive over Fixed Strong")
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/percentage_improvement.png")
    plt.show()

if __name__ == "__main__":
    rows = load_summary()
    config_names, migration_probs, fixed_lats, adaptive_lats, fixed_oh, adaptive_oh = prepare_data(rows)

    # Bar charts
    plot_latency_bar(config_names, fixed_lats, adaptive_lats)
    plot_overhead_bar(config_names, fixed_oh, adaptive_oh)

    # Line plots
    plot_latency_line(migration_probs, fixed_lats, adaptive_lats)
    plot_overhead_line(migration_probs, fixed_oh, adaptive_oh)

    # Percentage improvement
    plot_percentage_improvement(config_names, fixed_lats, adaptive_lats, fixed_oh, adaptive_oh)