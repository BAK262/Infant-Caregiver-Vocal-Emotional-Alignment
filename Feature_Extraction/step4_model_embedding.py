import torch
import torch.nn as nn
import numpy as np
import datatable as dt
import os
import glob

"""
NOTE: the model used here is provided by the author of the paper "Quantifying Emotional Similarity in Speech".
Anyone who wants to use this code/model, please contact the original author.
""" 

# Set the path to the main folder
main_path = 'D:\Seafile\学术\Intern_UTokyo\project'
corpus = 'corpus_Edinburgh'
os.chdir(main_path)

class BaseNetwork(nn.Module):
    def __init__(self, *args, **kwargs):
        super(BaseNetwork, self).__init__()
        
        self.inp_bn = nn.BatchNorm1d(6373)
        self.fc = nn.ModuleList([
            nn.Sequential(
                nn.Linear(6373, 2048), nn.ReLU(),
                nn.Dropout(0.2), nn.BatchNorm1d(2048)
            ),
            nn.Sequential(
                nn.Linear(2048, 2048), nn.ReLU(),
                nn.Dropout(0.2), nn.BatchNorm1d(2048)
            ),
            nn.Sequential(
                nn.Linear(2048, 2048), nn.ReLU(),
                nn.Dropout(0.2), nn.BatchNorm1d(2048)
            ),
            nn.Sequential(
                nn.Linear(2048, 1024), nn.ReLU(),
                nn.Dropout(0.2), nn.BatchNorm1d(1024)
            ),
            nn.Sequential(
                nn.Linear(1024, 1024), nn.ReLU(),
                nn.Dropout(0.2), nn.BatchNorm1d(1024)
            ),
            nn.Sequential(
                nn.Linear(1024, 1024), nn.ReLU(),
                nn.Dropout(0.2), nn.BatchNorm1d(1024)
            )
        ])
        self.out = nn.Linear(1024, 512)

    def forward(self, x):
        h = self.inp_bn(x)
        for fc in self.fc:
            h = fc(h)
        o = self.out(h)
        return o

#7341 is length of test data
folder = os.path.join(main_path, "Feature_Extraction", "VAD_60")
total_weight_list = glob.glob(folder+"/*.pt")
weight_idx_list = []
total_weight_list.sort()
with open(os.path.join(folder, "val_loss.log"), 'r') as f:
    val_loss_list = []
    midx_list = []
    pre_midx = 0
    for line in f:
        midx = int(line[:-1].split("\t")[0])
        val_loss = float(line[:-1].split("\t")[1])
        val_loss_list.append(val_loss)
        midx_list.append(midx+pre_midx)
        if midx == 19000:
            pre_midx += 19238

    max_idx_list = np.flip(np.argsort(np.array(val_loss_list)))
    prev_idx_list = []
    for max_idx in max_idx_list:
        if max_idx in prev_idx_list:
            continue
        weight_idx_list.append(midx_list[max_idx])
        prev_idx_list.extend([max_idx-1, max_idx, max_idx+1])
        if len(weight_idx_list) == 5:
            break
weight_paths = [os.path.join(folder,"model_weights_"+str(widx)+".pt") for widx in weight_idx_list]

model_list = []
for wpath in weight_paths:
    cur_model = BaseNetwork()
    cur_model.load_state_dict(torch.load(wpath))
    cur_model.cuda()
    cur_model.eval()
    model_list.append(cur_model)

os.chdir(os.path.join(main_path,corpus,'audio_feature'))
feature_dt = dt.fread('feature_data.csv')
os.makedirs(os.path.join(main_path,corpus,'embedding'), exist_ok=True)
os.chdir(os.path.join(main_path,corpus,'embedding'))
embeddings = []
cnt = 0
for model in model_list:
    cnt = cnt+1
    sample = torch.Tensor(np.asarray(feature_dt[:,4:])).float().cuda()
    embedding = model(sample).detach().cpu().numpy()
    embedding_dt = feature_dt[:,0:4]
    embedding_dt.cbind(dt.Frame(embedding))
    embedding_dt.to_csv(f'model_{cnt}.csv')
    embeddings.append(embedding_dt)
