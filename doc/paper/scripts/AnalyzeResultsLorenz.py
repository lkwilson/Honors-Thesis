import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

from echonn.sys import SystemSolver

res = pickle.load(open('lorenz_results.p', 'rb'))
run, lce, ts_data, results = res

test_rmse = [rmse for _, _, _, (_, _, rmse) in results['best model rmse']]
test_rmse = np.array(test_rmse)


def rmse(d, y):
    num_samples = d.shape[0]
    return np.sqrt(np.sum((d-y)**2) / num_samples)


score = []
higher_score = []
for rmse_res in results['best model rmse']:
    ds_test, ys_test, total_rmse = rmse_res[3]
    for sub in range(ds_test.shape[0]):
        err = rmse(ds_test[:sub+1], ys_test[:sub+1])
        if err > .05:
            score.append(sub)
            break
    for sub in range(ds_test.shape[0]):
        err = rmse(ds_test[:sub+1], ys_test[:sub+1])
        if err > 1:
            higher_score.append(sub)
            break
dir_pre = os.path.join('..', 'images', 'lorenz')
slvr = SystemSolver(run['system'])
runt = deepcopy(run)
runt['results'].t = ts_data.t
runt['results'].y = ts_data.y.T
fig = slvr.plot3d(runt)
plt.savefig(os.path.join(dir_pre, 'full_differential.png'))

sorter = np.flip(np.argsort(score))
how_many = 10
for rank, i in enumerate(sorter[:how_many]):
    ds_test, ys_test, total_rmse = results['best model rmse'][i][3]
    print(i, total_rmse, results['params'][i])

    rmse_over_t = [rmse(ds_test[:sub+1], ys_test[:sub+1])
                   for sub in range(ds_test.shape[0])]

    plt.figure()
    plt.title('RMSE vs Lyapunov Time\nParam {} ; RMSE {}'.format(
        results['params'][i], total_rmse))
    t_adj = (ts_data.test_t - ts_data.test_t[0]) / lce[0]
    plt.plot(t_adj, rmse_over_t, 'o-')
    plt.plot(t_adj, np.zeros_like(t_adj))
    name = 'rank_{}_param_{}_rmse.png'.format(rank, i)
    plt.savefig(os.path.join(dir_pre, name))
    plt.close()

    runt['results'].t = ts_data.test_t
    runt['results'].y = ds_test.T
    fig = slvr.plot3d(runt)
    runt['results'].t = ts_data.test_t[:score[i]]
    runt['results'].y = ys_test[:score[i]].T
    slvr.plot3d(runt, fig)
    runt['results'].t = ts_data.test_t[score[i]:higher_score[i]]
    runt['results'].y = ys_test[score[i]:higher_score[i]].T
    slvr.plot3d(runt, fig)
    plt.legend(['actual', 'approximated', 'deviation'])
    plt.title('Model Approximation\nParam {} ; RMSE {}'.format(
        results['params'][i], total_rmse))
    plt.tight_layout()
    name = 'rank_{}_param_{}_fit.png'.format(rank, i)
    plt.savefig(os.path.join(
        dir_pre, name))
    plt.close()
    # plt.show(True)


def plot_one(ind):
    ds_test, ys_test, total_rmse = results['best model rmse'][ind][3]
    plt.show(True)


def plot_res():
    for i, rmse in enumerate(results['best model rmse']):
        test_rmse = rmse[3]
        ds_test, ys_test, total_rmse = test_rmse

        rerr = np.mean((ys_test - ds_test) / ds_test, axis=1)
        rerr = np.sqrt(rerr**2)

        plt.figure()
        plt.title('Param Config {} RMSE: {}'.format(
            results['params'][i], total_rmse))
        plt.plot((ts_data.test_t - ts_data.test_t[0]) / lce[0], rerr)

        slvr = SystemSolver(run['system'])
        runt = deepcopy(run)
        runt['results'].t = ts_data.test_t
        runt['results'].y = ds_test.T
        slvr.plotnd(runt)
        runt['results'].t = ts_data.test_t
        runt['results'].y = ys_test.T
        slvr.plotnd(runt)
        slvr.plot3d(runt)
        plt.title('Param Config {} RMSE: {}'.format(
            results['params'][i], total_rmse))
        plt.show(True)
