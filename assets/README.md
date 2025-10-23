# Client Segmentation Banking App

## 1. Project Overview

This project is an end-to-end web application for customer segmentation in the banking sector. It provides a complete pipeline from raw data ingestion to actionable business insights, leveraging machine learning techniques for robust analysis. The platform enables users to upload customer data, automatically clean and preprocess it, perform dimensionality reduction using Principal Component Analysis (PCA), segment customers using both KMeans and Hierarchical clustering, and finally, generate AI-driven marketing recommendations.

The application is designed to be a powerful tool for data scientists, marketing analysts, and business strategists to understand customer behavior, identify distinct population segments, and tailor marketing strategies for improved engagement and profitability.

---

## 2. Mathematical Foundations

### Data Preprocessing

#### Interquartile Range (IQR) for Outlier Detection

Outliers are identified as data points that fall outside a specified range of the data's distribution. The IQR method is a robust statistical technique for this purpose.

1.  **Calculate Quartiles**: Find the first quartile (Q1), the 25th percentile, and the third quartile (Q3), the 75th percentile.
2.  **Calculate IQR**: The Interquartile Range is the difference between Q3 and Q1.
    $$ IQR = Q3 - Q1 $$
3.  **Define Boundaries**: The lower and upper bounds for outlier detection are defined as:
    $$ \text{Lower Bound} = Q1 - 1.5 \times IQR $$
    $$ \text{Upper Bound} = Q3 + 1.5 \times IQR $$

Any data point $x$ such that $x < \text{Lower Bound}$ or $x > \text{Upper Bound}$ is considered an outlier. In this application, outliers are capped at these bounds (a technique called winsorization) to preserve data integrity without removing rows.

#### Pearson's Correlation Coefficient (r)

Correlation measures the linear relationship between two continuous variables. The correlation heatmap visualizes these relationships for all pairs of numeric features.

For two variables $X$ and $Y$, the Pearson correlation coefficient is:

$$ r = \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i - \bar{x})^2 \sum_{i=1}^{n}(y_i - \bar{y})^2}} $$

Where:
- $n$ is the number of samples.
- $x_i, y_i$ are the individual sample points.
- $\bar{x}, \bar{y}$ are the mean values of $X$ and $Y$.

The value of $r$ ranges from -1 (perfect negative correlation) to +1 (perfect positive correlation), with 0 indicating no linear correlation.

### Dimensionality Reduction

#### Principal Component Analysis (PCA)

PCA is a linear dimensionality reduction technique that transforms a set of correlated variables into a smaller set of uncorrelated variables called principal components.

1.  **Standardization**: The data is first standardized to have a mean of 0 and a standard deviation of 1.
2.  **Covariance Matrix**: The covariance matrix $\Sigma$ of the standardized data is computed.
3.  **Eigenvalue Decomposition**: The eigenvalues ($\λ$) and eigenvectors ($v$) of the covariance matrix are calculated.
    $$ \Sigma v = \lambda v $$
4.  **Principal Components**: The eigenvectors, ordered by their corresponding eigenvalues from largest to smallest, represent the directions of maximum variance and are the principal components. The eigenvalues represent the magnitude of variance captured by each component.
5.  **Component Selection**: The number of components is chosen such that a desired amount of cumulative variance is explained (e.g., 80%).

### Clustering Algorithms

#### KMeans Clustering

KMeans is an iterative algorithm that partitions a dataset into a predefined number of clusters ($k$).

**Objective Function**: To minimize the within-cluster sum of squares (WCSS), also known as inertia.

$$ \underset{S}{\operatorname{arg\,min}} \sum_{i=1}^{k} \sum_{x \in S_i} \|x - \mu_i\|^2 $$

Where:
- $S_i$ is the set of points in cluster $i$.
- $\mu_i$ is the centroid (mean) of cluster $i$.

**Algorithm**:
1.  **Initialization**: Randomly select $k$ data points as initial centroids.
2.  **Assignment Step**: Assign each data point to the cluster with the nearest centroid.
3.  **Update Step**: Recalculate the centroids as the mean of all points assigned to each cluster.
4.  **Iteration**: Repeat steps 2 and 3 until the cluster assignments no longer change.

#### Hierarchical Clustering

Hierarchical clustering builds a hierarchy of clusters, either agglomerative (bottom-up) or divisive (top-down). This app uses the agglomerative approach.

**Algorithm**:
1.  **Initialization**: Treat each data point as a single cluster.
2.  **Merge Step**: Iteratively merge the two closest clusters based on a linkage criterion.
3.  **Hierarchy**: Repeat until only one cluster remains.

**Linkage Methods**: Define the distance between clusters.
- **Ward's Method**: Merges clusters in a way that minimizes the increase in the total within-cluster variance. This is the method used in the application.

### Evaluation Metrics

#### Silhouette Score

The Silhouette Score measures how similar a data point is to its own cluster compared to other clusters. It provides a measure of cluster cohesion and separation.

For a single data point $i$:

$$ s(i) = \frac{b(i) - a(i)}{\max\{a(i), b(i)\} } $$

Where:
- $a(i)$: The average distance from point $i$ to all other points in the same cluster.
- $b(i)$: The average distance from point $i$ to all points in the nearest neighboring cluster.

The overall Silhouette Score is the average $s(i)$ for all data points. The score ranges from -1 to +1, where a high value indicates that the object is well matched to its own cluster and poorly matched to neighboring clusters.

---

## 3. Methodological Justifications

- **PCA**: Chosen for its effectiveness in reducing noise and multicollinearity, preparing the data for more stable clustering, and enabling 2D visualization.
- **KMeans**: A fast and efficient algorithm suitable for large datasets and identifying spherical clusters.
- **Hierarchical Clustering**: Provides a rich, hierarchical structure and does not require pre-specifying the number of clusters. The dendrogram is a powerful visualization tool.
- **Silhouette Score**: A robust, geometry-based metric that evaluates the quality of clusters without needing ground truth labels.
- **Ward's Linkage**: Tends to produce well-balanced and compact clusters, which is often desirable for customer segmentation.

---

## 4. Data Pipeline Workflow

1.  **Home**: Overview of the pipeline steps and project features.
2.  **Data Cleaning**: User uploads a CSV file. The backend automatically handles missing values (imputation), detects and caps outliers (IQR method), and displays data quality metrics and a correlation heatmap.
3.  **PCA Analysis**: The cleaned, scaled data is fed into PCA. The number of components explaining at least 80% of the variance is automatically selected. Scree and cumulative variance plots are generated.
4.  **Clustering**: The user selects an algorithm (KMeans or Hierarchical) and the number of clusters. The backend runs the algorithm on the PCA-transformed data. Results, including a scatter plot and silhouette scores, are displayed.
5.  **Customer Profiles**: Detailed profiles are generated for each cluster, including the number of customers, percentage of total, and top distinguishing features based on mean value deviations from the overall population.
6.  **Insights**: An AI-powered dashboard provides high-level KPIs, segment distribution charts, and actionable marketing recommendations for each customer segment.

---

## 5. Implementation Details

- **Backend**: Python with Reflex framework. State management is handled through various `rx.State` classes, each dedicated to a specific step of the pipeline.
- **Data Processing**: `pandas` and `numpy` are used for data manipulation. `scikit-learn` provides the implementations for `StandardScaler`, `PCA`, `KMeans`, and `AgglomerativeClustering`.
- **Visualization**: `matplotlib` and `seaborn` are used on the backend to generate static plots (heatmap, dendrogram), which are saved as images and served to the frontend. Interactive charts on the frontend are built using `recharts`.

### Code Snippet: PCA Execution

# From app/states/pca_state.py

# Standardize data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df_numeric)

# Determine optimal number of components
pca = PCA()
pca.fit(scaled_data)
cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
n_components = np.where(cumulative_variance >= 0.8)[0][0] + 1

# Run final PCA
pca = PCA(n_components=n_components)
pca_result = pca.fit_transform(scaled_data)


---

## 6. Clustering Evaluation

- **Silhouette Score**: The primary metric used. A score close to +1 indicates dense and well-separated clusters. A score near 0 indicates overlapping clusters. A negative score suggests that samples may have been assigned to the wrong cluster.
- **Visual Inspection**: The PCA scatter plot allows for a visual assessment of cluster separation. The dendrogram helps visualize the hierarchical relationships and decide on a natural number of clusters.

---

## 7. Business Insights Generation

The final step translates complex statistical results into clear business actions:
1.  **Identify Key Features**: For each segment, the features with the highest deviation from the population mean are identified (e.g., "High Income, Low Spending").
2.  **Create Personas**: Segments are given descriptive labels (e.g., "Affluent Savers," "Active Spenders").
3.  **Generate Recommendations**: Based on the persona, a rule-based engine generates marketing recommendations. For example, a high-income segment might receive recommendations for investment products, while a high-spending segment might be targeted with loyalty programs.

---

## 8. Installation & Usage

1.  **Clone the repository**.
2.  **Install dependencies**:
    bash
    pip install -r requirements.txt
    
3.  **Initialize the Reflex app**:
    bash
    reflex init
    
4.  **Run the app**:
    bash
    reflex run
    
5.  Open your browser and navigate to `http://localhost:3000`.

---

## 9. Tech Stack

- **Web Framework**: [Reflex](https://reflex.dev/) (Python)
- **Machine Learning**: [scikit-learn](https://scikit-learn.org/)
- **Data Manipulation**: [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/)
- **Static Visualization**: [matplotlib](https://matplotlib.org/), [seaborn](https://seaborn.pydata.org/)
- **Interactive Visualization**: [recharts](https://recharts.org/)
- **Frontend**: Reflex Components, TailwindCSS

---

## 10. Future Enhancements

- **Advanced Clustering**: Implement more advanced algorithms like DBSCAN or Gaussian Mixture Models (GMM).
- **Model Persistence**: Save and load trained models to re-apply segmentation to new data without retraining.
- **Interactive Visualizations**: Allow users to interactively select points on charts to see detailed customer information.
- **PDF Export**: Implement the "Download PDF Report" functionality for the insights dashboard.
- **Real-time Segmentation**: Integrate with a database or data stream for real-time customer analysis.
