# Replication Analysis (R)
# V-shaped trajectories across Original -> AI_Revised -> Author_Refined (N = 30).
# Requirements: readr, dplyr, ggplot2, tidyr

library(readr)
library(dplyr)
library(tidyr)
library(ggplot2)

# Run from the repository root, or adjust ROOT:
ROOT <- getwd()
stopifnot(file.exists(file.path(ROOT, "data", "vshape_30_clean_long.csv")))

df <- read_csv(file.path(ROOT, "data", "vshape_30_clean_long.csv"))
df$Stage <- factor(df$Stage, levels = c("Original", "AI_Revised", "Author_Refined"))

metrics <- c("MTLD", "MLU", "Cohesion_Score", "SBERT_Similarity")

# Descriptives by stage
df %>% group_by(Stage) %>%
  summarise(across(all_of(metrics), list(mean = mean, sd = sd)), .groups = "drop") %>%
  print()

# Friedman test per metric (nonparametric repeated measures) + V-shaped contrast
for (m in metrics) {
  wide <- reshape(df[, c("Participant_ID", "Stage", m)], idvar = "Participant_ID",
                  timevar = "Stage", direction = "wide")
  fm <- friedman.test(as.matrix(wide[, -1]))
  contrast <- wide[[paste0(m, ".Original")]] + wide[[paste0(m, ".Author_Refined")]] -
              2 * wide[[paste0(m, ".AI_Revised")]]
  wt <- wilcox.test(contrast)
  cat(sprintf("%s: Friedman chi2 = %.3f, p = %.5f | V-contrast mean = %.3f, Wilcoxon p = %.5f\n",
              m, fm$statistic, fm$p.value, mean(contrast), wt$p.value))
}

# 4-panel trajectory figure: individual lines + mean +/- 95% CI
long_df <- df %>% pivot_longer(all_of(metrics), names_to = "Metric", values_to = "value")
summ <- df %>% group_by(Stage) %>%
  summarise(across(all_of(metrics), list(mean = mean, sd = sd, n = length)),
            .groups = "drop") %>%
  pivot_longer(-Stage, names_to = c("Metric", "stat"), names_pattern = "(.*)_(mean|sd|n)") %>%
  pivot_wider(names_from = stat, values_from = value) %>%
  mutate(ci = 1.96 * sd / sqrt(n))

p <- ggplot() +
  geom_line(data = long_df, aes(Stage, value, group = Participant_ID),
            colour = "grey", alpha = 0.25) +
  geom_ribbon(data = summ, aes(Stage, ymin = mean - ci, ymax = mean + ci, group = Metric),
              fill = "crimson", alpha = 0.2) +
  geom_line(data = summ, aes(Stage, mean, group = Metric), colour = "crimson") +
  geom_point(data = summ, aes(Stage, mean), colour = "crimson") +
  facet_wrap(~Metric, scales = "free_y") +
  labs(title = "V-shaped trajectories across revision stages (N = 30)",
       x = NULL, y = "Score") +
  theme_minimal()

figdir <- file.path(ROOT, "figures")
dir.create(figdir, showWarnings = FALSE)
ggsave(file.path(figdir, "vshape_trajectories.png"), p, width = 11, height = 8, dpi = 300)
cat("Figure saved to figures/vshape_trajectories.png\n")
