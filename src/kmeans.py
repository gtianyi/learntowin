'''
Created on Nov 22, 2016

@author: Alison Paredes
'''

def kmeans(data, k):
    centroids = random_seed(data, k)
    clusters = None
    for i in range(10): #TODO: When to stop?
        clusters = [];
        for point in data:
            closest = 0
            for centroid, i in centroids:
                min_distance = distance(point, centroids[closest])
                if (compare_points(min_distance, distance(point, centroid)) < 0): #How are comparators usually defined?
                    clusters.append(point)
        point_length = len(data[0])
        centroids = new_centroids(clusters, point_length)
    return (clusters)

def new_centroids(clusters, point_length):
    centroids = []*len(clusters)
    for cluster,i in clusters:
        centroids[i] = point_length * [0.0]
        for point in cluster:
            centroids[i] = sum_points(centroids[i], point)
        centroids[i] = mean(centroids[i], len(cluster))
    return centroids

def mean(point, cluster_length):
    for i in range(len(point)):
        point[i] = point[i]/float(cluster_length)

def sum_points(point_a, point_b):
    difference=[]
    for i in range(len(point_a)):
        difference.append(point_a[i] + point_b[i])
    return difference

def random_seed(data, k):
    centroids = [];
    for i in range(k):
        centroids.append(data[i]) #TODO: Change to random seed
    return centroids

def distance(point_a, point_b):
    difference=[]
    for i in range(len(point_a)):
        difference.append(abs(point_a[i] - point_b[i]))
    return difference

def compare_points(point_a, point_b):
    sum_a = 0
    for a in point_a:
        sum_a += a
    sum_b = 0
    for b in point_b:
        sum_b += b
    return sum_a - sum_b


if __name__ == '__main__':
    data = []