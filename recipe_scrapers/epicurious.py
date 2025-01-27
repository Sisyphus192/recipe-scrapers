import re


from ._abstract import AbstractScraper
from ._utils import normalize_string, get_yields


class Epicurious(AbstractScraper):
    fork_rating_re = re.compile('/(\d)_forks.png')

    @classmethod
    def host(self):
        return 'epicurious.com'

    def title(self):
        return self.soup.find(
            'h1',
            {'itemprop': 'name'}
        ).get_text()

    def total_time(self):
        return 0

    def yields(self):
        return get_yields(self.soup.find(
            'dd',
            {'itemprop': 'recipeYield'}
        ))

    def image(self):
        image = self.soup.find(
            'img',
            {'class': 'photo', 'srcset': True}
        )
        return image['srcset'] if image else None

    def ingredients(self):
        ingredients = self.soup.findAll(
            'li',
            {'itemprop': "ingredients"}
        )

        return [
            normalize_string(ingredient.get_text())
            for ingredient in ingredients
        ]

    def instructions(self):
        instructions = self.soup.findAll(
            'li',
            {'class': 'preparation-step'}
        )

        return '\n'.join([
            normalize_string(instruction.get_text())
            for instruction in instructions
        ])

    def avg_rating(self):
        rating = self.soup.find('meta', {'itemprop': 'ratingValue'})
        rating = rating["content"] if rating is not None else None
        rating = float(rating) if rating is not None else None
        return rating

    def best_rating(self):
        rating = self.soup.find('meta', {'itemprop': 'bestRating'})
        rating = rating["content"] if rating is not None else None
        rating = float(rating) if rating is not None else None
        return rating

    def worst_rating(self):
        rating = self.soup.find('meta', {'itemprop': 'worstRating'})
        rating = rating["content"] if rating is not None else None
        rating = float(rating) if rating is not None else None
        return rating

    def prepare_again_rating(self):
        rating = self.soup.find('div', {'class': 'prepare-again-rating'})
        rating = rating.find('span')
        rating = rating.get_text().strip() if rating is not None else None
        rating = float(rating.strip("%"))/100.0 if rating is not None else None
        return rating

    def num_reviews(self):
        rating = self.soup.find('span', {'class': 'reviews-count'})
        rating = rating.get_text().strip() if rating is not None else None
        rating = float(rating) if rating is not None else None
        return rating

    def reviews(self):
        reviews = self.soup.findAll('', {'class': "most-recent"})
        ratings = [rev.find('img', {'class': "fork-rating"}) for rev in reviews]
        temp = []
        for rating in ratings:
            if 'src' in rating.attrs:
                txt = rating.attrs['src']
            else:
                txt = ''
            rating = self.fork_rating_re.search(txt)
            rating = rating.group(1) if rating is not None else '0'
            rating = int(rating) if rating != '0' else None
            temp.append(rating)
        ratings = temp
        review_texts = [rev.find('div', {'class': "review-text"}) for rev in reviews]
        reviews = [rev.get_text().strip('/ flag if inappropriate') for rev in review_texts]
        result = [{'review_text': rt, "rating": rating}
                  for rt, rating in zip(reviews, ratings)]
        return result

    def tags(self):
        tags = self.soup.findAll(
            'dt',
            {'itemprop': 'recipeCategory'}
        )

        return [
            normalize_string(tag.get_text())
            for tag in tags
        ]
