setwd("~/Google Drive/GitHub/Insight/object_detection/feature_extraction")
library(tidyverse)
library(viridis)

# Load ANNOY results output from Python/Pandas
df <- read.csv('annoy_results.csv')

# Identify correct and incorrect identifications; compute Similarity
df$Correct <- with(df, ifelse(Predicted_Index == Original_Index, 1, 0))
df$Similarity <- 1 - df$Distance

# Bin cosine results
cut_seq <- seq(-1, 2, 1)
df$bin <- cut(df$Similarity, breaks = cut_seq)
df$Dist_bin <- cut(df$Distance, breaks = cut_seq)

# Get/bin cosine distances for identified versus real images from Python/Pandas         
aug_ref_cos_dist <- read.table('aug_ref_cos_distance.txt', header = F)
aug_ref_cos_dist <- as.vector(aug_ref_cos_dist$V1)
df$aug_ref_dist <- aug_ref_cos_dist
df$aug_ref_sim <- 1 - df$aug_ref_dist
df$aug_ref_sim_bins <- cut(df$aug_ref_sim, cut_seq)

# orig_file_list <- scan("augmenter_original_file_list.txt", what = 'character')

summary_df <- df %>%
  group_by(aug_ref_sim_bins) %>%
  summarize(
    mean_accuracy = mean(Correct),
    num_obs = n(),
    SD = sd(Correct)
  )

summary_df$Percent_improvement_chance <- summary_df$mean_accuracy/chance

weighted.mean(summary_df$Percent_improvement_chance, summary_df$num_obs)

q <- ggplot(summary_df, aes(aug_ref_sim_bins, Percent_improvement_chance, size = num_obs)) + 
  geom_point() + 
  theme_minimal() + xlab("Picture Similarity") + 
  ylab("% Improvement Over Chance") 
q

# ---- Plot classification metrics (F1 score)
metrics = read.csv('category_classification_scores.csv')

top10_cols <- viridis(n = 10, end = .7, direction = -1)

top10 = metrics[1:10,]
bottom10 = metrics[(nrow(metrics)-9):nrow(metrics), ]

top10$Category <- factor(top10$Category, levels = top10$Category)

top10_plot = ggplot(top10, aes(Category, f1.score, fill = Category)) +
  geom_bar(stat = "identity") + theme_minimal() +
  ylim(c(0, 1)) + ylab("F1 Score") + scale_x_discrete(limits = top$Category) +
  scale_fill_manual(values = top10_cols, guide = F) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  geom_hline(yintercept = .5, lty = 2, col = "grey")

top10_plot
ggsave("F1_top.pdf", width = 7, height = 4)

bottom10$Category <- factor(bottom10$Category, levels = bottom10$Category)
bottom_cols <- plasma(n = 10, end = .7)

bottom10_plot <- ggplot(bottom10, aes(Category, f1.score, fill = Category)) +
  geom_bar(stat = "identity") + theme_minimal() +
  ylim(c(0, 1)) + ylab("F1 Score") + scale_x_discrete(limits = bottom10$Category) +
  scale_fill_manual(values = bottom_cols, guide = F) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  geom_hline(yintercept = .5, lty = 2, col = "grey")
bottom10_plot

ggsave("F1_bottom.pdf", width = 7, height = 4)

# Get weighted mean F1 score
weighted_F1_mean <- weighted.mean(metrics$f1.score, metrics$support)
weighted_F1_mean


# Plot two good and two bad examples
two_cols <- viridis(5, end = .5, direction = -1, alpha =.9)
# 5th category is to make space; will delete later
short_df <- metrics[metrics$Category %in% c("Chambord", "Vodka", "Rum", "Creme de Cacao", "Soju"),]                    

short_df$Category <- factor(short_df$Category, levels = short_df$Category)

short_plot <- ggplot(short_df, aes(Category, f1.score, fill = Category)) +
  geom_bar(stat = "identity") + theme_minimal() +
  ylim(c(0, 1)) + ylab("F1 Score") + scale_x_discrete(limits = short_df$Category) +
  scale_fill_manual(values = two_cols, guide = F) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
short_plot
