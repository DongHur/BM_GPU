import numpy as np
import matplotlib, random, yaml
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
from tqdm import tqdm
import skvideo.io
from glob import glob

def main():
    result_path = "results/round2_legs_antennae"

    # Load Config Files
    with open(f"{result_path}/INFO.yaml") as f:
        INFO = yaml.load(f, Loader=yaml.FullLoader)
        INFO_values = list(INFO.values())
        INFO_values.sort(key=lambda x: x['order'])  
    config_path = "."
    with open(f"{config_path}/config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Format Data
    tot_bp, tot_bp_scaled, tot_angles, tot_rotations, tot_power, tot_embed, tot_clusters = [], [], [], [], [], [], []
    for file in tqdm(INFO_values):
        tot_bp.append( np.load(f"{file['directory']}/bodypoints.npy") )
        tot_bp_scaled.append( np.load(f"{file['directory']}/scaled_bodypoints.npy") )
        tot_angles.append( np.load(f"{file['directory']}/angles.npy") )
        tot_power.append( np.load(f"{file['directory']}/power.npy") )
        tot_embed.append( np.load(f"{file['directory']}/embeddings.npy") )
        tot_clusters.append( np.load(f"{file['directory']}/clusters.npy") )
    tot_bp = np.concatenate(tot_bp)
    tot_bp_scaled = np.concatenate(tot_bp_scaled)
    tot_angles = np.concatenate(tot_angles)
    tot_power = np.concatenate(tot_power, axis=2)
    tot_embed = np.concatenate(tot_embed)
    tot_clusters = np.concatenate(tot_clusters)

    num_videos_per_clusters = 16

    # Determine Which frames to Abstract
    num_clusters = int(np.max(tot_clusters[:,0]).item()) + 1
    cluster_distribution = []
    for clust_i in range(num_clusters):
        clust_idx = np.where(tot_clusters[:,0] == clust_i)[0]
        cluster_distribution.append(len(clust_idx))

    video_cluster_idx = {}
    for clust_i in range(num_clusters):
        clust_idx = np.where(tot_clusters[:,0] ==clust_i)[0]
        difference = np.diff(clust_idx)

        # Find consecutive break
        break_idx = np.where(difference != 1)[0]
        mod_break_idx = np.insert(break_idx, 0, 0)
        break_difference = np.diff(mod_break_idx)

        # Find max consecutive
        sorted_idx = np.argsort(break_difference)
        top_idx = sorted_idx[-num_videos_per_clusters:]
        video_idx = np.array([[ clust_idx[mod_break_idx[idx]+1], clust_idx[mod_break_idx[idx+1]+1]] for idx in top_idx])
        video_cluster_idx[clust_i] = video_idx

    # Create video
    fig, ax = plt.subplots(4,4,figsize=(10,10))
    ang_palette = sns.color_palette('tab10', 10)

    # video format        
    FFMpegWriter = animation.writers['ffmpeg']
    writer = FFMpegWriter(fps=10)
    save_path="videos/test.mp4"
    with writer.saving(fig, save_path, dpi=300):
        for fr_i in tqdm(np.arange(0, 100), desc="Frame Loop"):
            for i, (start, stop) in tqdm(video_cluster_idx[2]):
                ax[i//4,i%4].clear()
                ax[i//4,i%4].set_axis_off()
                ax[i//4,i%4].set(xlim=(-3,3), ylim=(-3,3))

                bp_linewidth = 2
                bp_markersize = 3
                alpha = 0.8
                fr, shadow_i = start+fr_i, 0

                # left side
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,0:4,0], tot_bp_scaled[fr+shadow_i,0:4,1], 
                         c='k', alpha=alpha, 
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,5:8,0], tot_bp_scaled[fr+shadow_i,5:8,1], 
                         c=ang_palette[0], alpha=alpha, 
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,8:11,0], tot_bp_scaled[fr+shadow_i,8:11,1], 
                         c=ang_palette[1], alpha=alpha, 
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,11:14,0], tot_bp_scaled[fr+shadow_i,11:14,1], 
                         c=ang_palette[2], alpha=alpha, 
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,14:17,0], tot_bp_scaled[fr+shadow_i,14:17,1], 
                         c=ang_palette[3], alpha=alpha, 
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                # right side
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,18:21,0], tot_bp_scaled[fr+shadow_i,18:21,1], 
                         c=ang_palette[4], alpha=alpha,
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,21:24,0], tot_bp_scaled[fr+shadow_i,21:24,1], 
                         c=ang_palette[5], alpha=alpha,
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,24:27,0], tot_bp_scaled[fr+shadow_i,24:27,1], 
                         c=ang_palette[6], alpha=alpha,
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)
                ax[i//4,i%4].plot(tot_bp_scaled[fr+shadow_i,27:30,0], tot_bp_scaled[fr+shadow_i,27:30,1], 
                         c=ang_palette[7], alpha=alpha,
                         marker="o", linewidth=bp_linewidth, markersize=bp_markersize)

            writer.grab_frame()
        plt.close()

if __name__ == "__main__":
    main()