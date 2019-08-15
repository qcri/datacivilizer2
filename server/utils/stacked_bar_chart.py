import numpy as np
import matplotlib.pyplot as plt

# Used in mod_balance
def plot_stacked_bar_chart(save_path, other_kept, other_removed, rest):

    N = 3

    tot = []
    r = []
    ok = []
    orm = []
    kept = []
    for i in range(N):
        tot.append(rest[i]+other_kept[i]+other_removed[i])
        r.append((100*rest[i])/tot[i])
        ok.append((100*other_kept[i])/tot[i])
        orm.append((100*other_removed[i])/tot[i])
        kept.append(r[i]+ok[i])

    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, r, width, color='b')
    p2 = plt.bar(ind, ok, width, bottom=r, color='g')
    p3 = plt.bar(ind, orm, width, bottom=kept, color='r')

    plt.ylabel('Number of segments')
    plt.title('Number of segments kept or removed in training, testing and validation sets')
    plt.xticks(ind, ('Train', 'Test', 'Validation'))
    plt.yticks(np.arange(0, 101, 20), ('0%', '20%', '40%', '60%', '80%', '100%'))
    plt.legend((p2[0], p3[0], p1[0]), ('Others kept', 'Others removed', 'Rest kept'))

    plt.savefig('./Data/' + save_path)

# Used in mod_crop
def plot_stacked_bar_chart_2(save_path, non_zero, all_zero):

    N = 3

    tot = []
    nz = []
    az = []
    for i in range(N):
        tot.append(non_zero[i]+all_zero[i])
        nz.append((100*non_zero[i])/tot[i])
        az.append((100*all_zero[i])/tot[i])

    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, nz, width, color='g')
    p2 = plt.bar(ind, az, width, bottom=nz, color='r')

    plt.ylabel('Number of segments')
    plt.title('Number of non zero (kept) and all zero (removed) segments')
    plt.xticks(ind, ('Train', 'Test', 'Validation'))
    plt.yticks(np.arange(0, 101, 20), ('0%', '20%', '40%', '60%', '80%', '100%'))
    plt.legend((p1[0], p2[0]), ('Non zero segments (kept)', 'All zero segments (removed)'))

    plt.savefig('./Data/' + save_path)

def main():
    rest = [15, 82, 49]
    others_kept = [2043, 1243, 923]
    others_removed = [2134, 1093, 923]

    plot_stacked_bar_chart("test.jpg", others_kept, others_removed, rest)
    plot_stacked_bar_chart_2("test_2.jpg", others_kept, others_removed)

if __name__ == '__main__':
    main()