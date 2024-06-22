from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from store.models import Product
from category.models import Category
from user_interaction.models import UserInteraction
from django.db.models import Count
import random

def get_recommendations(user_id, k=20):
    # Fetching user interactions
    user_interactions = UserInteraction.objects.filter(user_id=user_id)

    # Fetch the product IDs the user interacted with
    product_ids = user_interactions.values_list('product_id', flat=True)
    
    num_interactions = len(product_ids)
    
    if num_interactions == 0:  # No interactions
        recommended_product_ids = random.sample(list(Product.objects.all().values_list('id', flat=True)), 20)
    elif num_interactions == 1:  # Single interaction
        # Get the brand and category of the single interaction
        product_info = Product.objects.get(id=product_ids[0])
        brand = product_info.brand
        category_id = product_info.category_id
        
        # Get products with the same brand and category excluding the interacted product
        similar_products = Product.objects.filter(brand=brand, category_id=category_id).exclude(id__in=product_ids)
        similar_product_ids = similar_products.values_list('id', flat=True)[:100]  # Limit to 100 similar products

        if len(similar_product_ids) < k:
            additional_products = Product.objects.filter(category_id=category_id).exclude(id__in=product_ids)
            additional_product_ids = additional_products.values_list('id', flat=True)[:k - len(similar_product_ids)]
            similar_product_ids = list(similar_product_ids) + list(additional_product_ids)
        
        # TF-IDF vectorization for brand and category features
        combined_features = [f"{brand} {Category.objects.get(id=category_id).category_name}" for _ in similar_product_ids]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(combined_features)
        
        # Train k-NN model using the TF-IDF matrix
        knn_model = NearestNeighbors(n_neighbors=k, metric='cosine')
        knn_model.fit(tfidf_matrix)
        
        # Find k nearest neighbors among the similar products
        _, indices = knn_model.kneighbors(tfidf_matrix)
        recommended_product_ids = [similar_product_ids[int(idx)] for idx in indices[0]]
    else:  # Multiple interactions
        # Find the most interacted product
        most_interacted_product = UserInteraction.objects.filter(user_id=user_id).values('product_id').annotate(interaction_count=Count('product_id')).order_by('-interaction_count').first()
        most_interacted_product_id = most_interacted_product['product_id']
        
        # Get the brand and category of the most interacted product
        product_info = Product.objects.get(id=most_interacted_product_id)
        brand = product_info.brand
        category_id = product_info.category_id
        
        # Get products with the same brand and category excluding the interacted product
        similar_products = Product.objects.filter(brand=brand, category_id=category_id).exclude(id__in=product_ids)
        similar_product_ids = similar_products.values_list('id', flat=True)[:100]  # Limit to 100 similar products

        if len(similar_product_ids) < k:
            additional_products = Product.objects.filter(category_id=category_id).exclude(id__in=product_ids)
            additional_product_ids = additional_products.values_list('id', flat=True)[:k - len(similar_product_ids)]
            similar_product_ids = list(similar_product_ids) + list(additional_product_ids)
        
        # TF-IDF vectorization for brand and category features
        combined_features = [f"{brand} {Category.objects.get(id=category_id).category_name}" for _ in similar_product_ids]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(combined_features)
        
        # Train k-NN model using the TF-IDF matrix
        knn_model = NearestNeighbors(n_neighbors=k, metric='cosine')
        knn_model.fit(tfidf_matrix)
        
        # Find k nearest neighbors among the similar products
        _, indices = knn_model.kneighbors(tfidf_matrix)
        recommended_product_ids = [similar_product_ids[int(idx)] for idx in indices[0]]
    
    return list(recommended_product_ids)
