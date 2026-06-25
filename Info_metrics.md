# PPO Training Metrics

| Metrics | Mô tả | Tăng | Giảm |
|---|---|---|---|
| `ep_rew_mean` | Tổng reward trung bình mỗi episode (100 episode gần nhất) | Agent học tốt hơn, tiến xa hơn, chết ít hơn | Agent đang quên hoặc reward function có vấn đề |
| `ep_len_mean` | Số bước trung bình mỗi episode | Agent sống lâu hơn (cần kết hợp với reward để đánh giá) | Agent chết sớm hoặc bị timeout ít hơn |
| `fps` | Số frame xử lý mỗi giây | Throughput tốt, huấn luyện nhanh hơn | Bottleneck CPU/GPU hoặc quá nhiều môi trường |
| `iterations` | Số lần cập nhật rollout buffer đã thực hiện | — | — |
| `time_elapsed` | Thời gian đã chạy (giây) | — | — |
| `total_timesteps` | Tổng số bước môi trường đã thu thập | — | — |
| `explained_variance` | Mức độ value network dự đoán được returns thực tế (lý tưởng gần 1.0) | Value network tốt hơn, baseline ổn định, gradient ít noise | Value network kém, học không ổn định; nếu âm thì hoàn toàn sai |
| `approx_kl` | Mức độ policy thay đổi sau mỗi update (lý tưởng: 0.01–0.03) | Policy thay đổi quá mạnh, có nguy cơ mất ổn định | Policy gần như không thay đổi, có thể đang hội tụ hoặc lr quá nhỏ |
| `clip_fraction` | Tỉ lệ gradient bị clip bởi epsilon (lý tưởng: 0.1–0.2) | Policy update quá lớn, nên giảm lr hoặc num_epochs | Policy thay đổi nhỏ, ổn định nhưng có thể học chậm |
| `clip_range` | Giá trị epsilon PPO clipping (hyperparameter cố định) | — | — |
| `entropy_loss` | Độ đa dạng action (âm vì SB3 minimize −entropy; lý tưởng không quá thấp) | Agent explore nhiều hơn | Agent bị collapse vào ít action — tăng beta nếu xuống quá thấp |
| `loss` | Tổng loss = policy loss + value loss + entropy loss | Bất thường nếu tăng đột biến (reward spike hoặc lr cao) | Bình thường nếu giảm đều theo thời gian |
| `policy_gradient_loss` | Loss của policy network (thường âm trong PPO) | Policy đang được cập nhật mạnh | Policy gần hội tụ tại vùng hiện tại |
| `value_loss` | Loss của value network (MSE giữa predicted và actual returns) | Value network dự đoán kém hoặc returns có phương sai lớn | Value network đang cải thiện dự đoán |
| `learning_rate` | Learning rate hiện tại | — | — |
| `n_updates` | Tổng số lần gradient update đã thực hiện | — | — |
