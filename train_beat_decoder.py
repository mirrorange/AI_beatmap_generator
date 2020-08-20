import sys,os,shutil
import json
from torch import optim
import random
from model import *
from torch.utils.tensorboard import SummaryWriter

savepath = sys.argv[1]
backuppath = sys.argv[2]
datasetpath = sys.argv[3]
learning_rate = float(sys.argv[4])
epochnum = int(sys.argv[5])
os.mkdir(os.path.join(backuppath,"beat_decoder"))
writer = SummaryWriter(log_dir="./log")

with open(datasetpath, "r") as f:
    dataset = json.load(f)
X1 = dataset['X1']
Y1 = dataset['Y1']


# 键形列表
jx_list = []
with open("glove/vocab.txt", "r") as f:
    for line in f.readlines():
        num = line.split(" ")[0]
        jx_list.append(int(num))


embedding = nn.Embedding.from_pretrained(get_glove_embedding(16, "vectors.txt"), freeze=False)
# print(embedding.dtype)

hidden_size = 128
encoder = EncoderRNN(hidden_size).to(device)
decoder = DecoderRNN(embedding, hidden_size, 16).to(device)  # 判断键型

encoder_optimizer = optim.Adam(encoder.parameters(), lr=learning_rate)
decoder_optimizer = optim.Adam(decoder.parameters(), lr=learning_rate)

criterion = nn.NLLLoss()

step = 0
for epoch in range(epochnum):
    total_loss = 0
    for i in range(1000):
        index = random.randrange(0, len(X1))
        x1 = torch.from_numpy(np.array(X1[index])).to(device).float()
        y1 = torch.from_numpy(np.array(Y1[index])).to(device).long()

        max_length = len(X1)

        encoder_optimizer.zero_grad()
        decoder_optimizer.zero_grad()

        max_length = len(X1[index])

        loss = 0

        encoder_hidden = encoder.initHidden()
        for ei in range(max_length):
            _, encoder_hidden = encoder(
                x1[ei], encoder_hidden)

        # 判断是键形
        decoder_input = torch.tensor([[random.choice(jx_list)]], device=device)
        decoder_hidden = encoder_hidden
        for di in range(max_length):

            decoder_output, decoder_hidden = decoder(
                decoder_input, decoder_hidden)
            target = y1[di].view(-1)
            # print(decoder_output)
            # print(target)
            loss += F.nll_loss(decoder_output, target)
            decoder_input = target  # Teacher forcing

        loss.backward()
        encoder_optimizer.step()
        decoder_optimizer.step()

        total_loss += loss.item() / max_length
        step = step + 1
        if i % 20 == 0:
            avg_loss = total_loss / (i+1)
            now_loss = loss.item() / max_length
            writer.add_scalar("beat_decoder_avg_loss/train", avg_loss, step)
            writer.add_scalar("beat_decoder_now_loss/train", now_loss, step)
            print(f"Epoch: {epoch},i: {i},avg_loss:{avg_loss},loss:{now_loss}")

    # save models
    backupdir = os.path.join(backuppath,"beat_decoder",str(epoch - 1))
    os.mkdir(backupdir)
    for item in os.listdir(savepath):
        shutil.move(os.path.join(savepath,item),backupdir)
    torch.save(encoder, os.path.join(savepath,"beat_encoder.pth"))
    torch.save(decoder, os.path.join(savepath,"beat_decoder.pth"))
    print("模型已保存：",epoch)
    writer.flush()
