from graphene import ObjectType, String, Field, List, Schema, Int, Mutation, InputObjectType

class Director(ObjectType):
    full_name = String()


class Actor(ObjectType):
    full_name = String()
    appear_in = List(lambda: Movie)

    def resolve_appear_in(self, info):
        return get_appearances(self)

    def __eq__(self, other):
        return self.full_name == other.full_name


class Movie(ObjectType):
    name = String(required=True)
    duration_in_minutes = Int()
    director = Field(Director)
    actors = List(Actor)
    release_date = String()


class Query(ObjectType):
    movies = List(Movie)
    movie = Field(Movie, name=String(required=True))

    def resolve_movies(self, info):
        # print(info.context["request"].method)
        # print(info.context["request"].headers)
        return MOVIES

    def resolve_movie(self, info, name):
        return get_movie(name)


class MovieInput(InputObjectType):
    name = String(required=True)
    duration_in_minutes = Int(required=True)
    director = String(required=True)
    release_date = String(required=True)
    actors = List(String, required=True)


class AddMovie(Mutation):
    class Arguments:
        movie = MovieInput()

    # Return an existing ObjectType (Movie) instead of a mutation-specific type (AddMovie)
    Output = Movie
    # Sometimes we prefer to return a mutation-specific type like AddMovie, for example
    # when the existing ObjectType contains information that we don't want to reveal.
    # When that is the case, we define the output fields as attributes in the mutation-specific class.

    def mutate(self, info, movie):
        print(movie)
        m = Movie(name=movie.name, release_date=movie.release_date, duration_in_minutes=movie.duration_in_minutes,
                  director=Director(full_name=movie.director), actors=[Actor(full_name) for full_name in movie.actors])
        MOVIES.append(m)
        return m


class Mutation(ObjectType):
    # A mutation called "addMovie" is created and now is avaliable to the client with that name
    add_movie = AddMovie.Field()

def get_movie(name):
    for movie in MOVIES:
        if name == movie.name:
            return movie

    return None


def get_appearances(actor):
    return [movie for movie in MOVIES if actor in movie.actors]


LEO_DC = Actor(full_name="Leo DiCaprio")
KATE_W = Actor(full_name="Kate Winslet")
JAMES_C = Director(full_name="James Cameron")
MARTIN_C = Director(full_name="Martin Scorsese")
JONAH_H = Actor(full_name="Jonah Hill")
MARGOT_R = Actor(full_name="Margot Robbie")
ACTORS = [LEO_DC, KATE_W, JAMES_C, MARTIN_C, JONAH_H, MARGOT_R]

TITANIC = Movie(name="Titanic", duration_in_minutes=195, release_date="05-02-1998", director=JAMES_C,
           actors=[LEO_DC, KATE_W])
WOLF_WS = Movie(name="The Wolf of Wall Street", duration_in_minutes=180, release_date="25-12-2013",
           director=MARTIN_C, actors=[LEO_DC, JONAH_H, MARGOT_R])

MOVIES = [TITANIC, WOLF_WS]

schema = Schema(query=Query, mutation=Mutation)
