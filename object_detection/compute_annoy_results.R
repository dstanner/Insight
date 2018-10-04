setwd("~/Google Drive/GitHub/Insight/object_detection/feature_extraction")
library(tidyverse)
library(viridis)

df <- read.csv('annoy_results.csv')

df$Correct <- with(df, ifelse(Predicted_Index == Original_Index, 1, 0))
cut_seq <- seq(-1, 2, .05)

df$Similarity <- 1 - df$Distance
df$bin <- cut(df$Similarity, breaks = cut_seq)
df$Dist_bin <- cut(df$Distance, breaks = cut_seq)


df <- merge(df, foo, by = "bin")

summary_df <- df %>%
  group_by(Dist_bin) %>%
  summarize(
    mean_accuracy = mean(Correct),
    num_obs = n(),
    SD = sd(Correct)
    )

p <- ggplot(summary_df, aes(Dist_bin, mean_accuracy, size = num_obs, color = nums)) + 
  geom_point() + 
  theme_minimal() + xlab("Picture Similarity") + 
  ylab("Bottle identification accuracy") + scale_color_viridis(end = .7)
p
            
aug_ref_cos_dist <- read.table('aug_ref_cos_distance.txt', header = F)
aug_ref_cos_dist <- as.vector(aug_ref_cos_dist$V1)
df$aug_ref_dist <- aug_ref_cos_dist
df$aug_ref_sim <- 1 - df$aug_ref_dist

df$aug_ref_sim_bins <- cut(df$aug_ref_sim, cut_seq)

orig_file_list <- scan("augmenter_original_file_list.txt", what = 'character')

chance <- 1/length(orig_file_list)

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
  ylab("% Improvement Over Chance") #+ geom_hline(yintercept = 1000, lty = 2)
q

# ---- Plot classification metrics (F1 score)
metrics = read.csv('category_classification_scores.csv')

top_cols <- viridis(n = 10, end = .7, direction = -1)

top = metrics[1:10,]
bottom = metrics[(nrow(metrics)-9):nrow(metrics), ]

top$Category <- factor(top$Category, levels = top$Category)

top_plot = ggplot(top, aes(Category, f1.score, fill = Category)) +
  geom_bar(stat = "identity") + theme_minimal() +
  ylim(c(0, 1)) + ylab("F1 Score") + scale_x_discrete(limits = top$Category) +
  scale_fill_manual(values = top_cols, guide = F) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  geom_hline(yintercept = .5, lty = 2, col = "grey")

top_plot
ggsave("F1_top.pdf", width = 7, height = 4)

bottom$Category <- factor(bottom$Category, levels = bottom$Category)
bottom_cols <- plasma(n = 10, end = .7)

bottom_plot <- ggplot(bottom, aes(Category, f1.score, fill = Category)) +
  geom_bar(stat = "identity") + theme_minimal() +
  ylim(c(0, 1)) + ylab("F1 Score") + scale_x_discrete(limits = bottom$Category) +
  scale_fill_manual(values = bottom_cols, guide = F) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  geom_hline(yintercept = .5, lty = 2, col = "grey")
bottom_plot

ggsave("F1_bottom.pdf", width = 7, height = 4)

# Get weighted mean F1 score
weighted_F1_mean <- weighted.mean(metrics$f1.score, metrics$support)
weighted_F1_mean


# Plot two good and two bad
two_cols <- viridis(5, end = .5, direction = -1, alpha =.9)
short_df <- metrics[metrics$Category %in% c("Chambord", "Vodka", "Rum", "Creme de Cacao", "Soju"),]                    

short_df$Category <- factor(short_df$Category, levels = short_df$Category)

short_plot <- ggplot(short_df, aes(Category, f1.score, fill = Category)) +
  geom_bar(stat = "identity") + theme_minimal() +
  ylim(c(0, 1)) + ylab("F1 Score") + scale_x_discrete(limits = short_df$Category) +
  scale_fill_manual(values = two_cols, guide = F) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
short_plot
