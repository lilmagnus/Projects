import os, sys, spacy, time
from rdflib import Graph
from sklearn.feature_extraction.text import TfidfVectorizer
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# Setting the recursion limit for larger files.
sys.setrecursionlimit(5000)

# Models for processing. Here we are using the large model from spacy. If you would like a faster model use en_core_web_sm.
# If you want to use the smaller model the accuracy will be reduced.
nlp = spacy.load('en_core_web_lg')

# We use Sklearn model TfidfVectorizer to give a score on the text element in the graph as well as the spacy model.
# We found out that by combining models we can classify the graph more accurately.
vectorization = TfidfVectorizer(stop_words='english')

# Directories have been set. This can be changed without affecting the code.
knowledge_directory = 'knowledge_graph'

merging_graph = 'MergingGraph'

merging_g = {}
corpus_dict = {}
object_dict = {}
text = []
object_list = []
knowledge_path = []
temp_sim_graph = []
to_del = []


# The function will get all the paths to all files from the path to knowledge_graph, and remove empty files.
# knowledge_directory is currently set to knowledge_graph. This can be edited without effecting the code.
def file_handler():
    for filename in os.listdir(knowledge_directory):
        graphs = os.path.join(knowledge_directory, filename)
        filesize = os.path.getsize(graphs)
        # Removing empty files
        if filesize == 2:
            pass
        elif os.path.isfile(graphs):
            knowledge_path.append(graphs)
        if len(knowledge_path) > 0:
            graph_maker()


def graph_maker():
    global g
    if len(knowledge_path) > 0:
        g = knowledge_path[-1]
        g = Graph()
        g.parse(location=knowledge_path[-1], format="turtle")
        graph_shredder()


# Parsing all elements of the graph, and filtering out what we do not want. We are only using unique elements.
# The elements are added to a hash table for faster accessibility.
def graph_shredder():
    global g
    if len(knowledge_path) > 0:
        knowledge_path.sort()
        object_dict[knowledge_path[-1]] = []
        for subject, predicate, object in g:
            if format(predicate) == "https://newshunter.uib.no/term#originalText":
                text.append(object[:])
                continue
            object_list.append(object[:])
            object_list.sort()
        for element in object_list:
            if element.startswith('ub') or element.startswith('https://newshunter'):
                continue
            else:
                object_dict[knowledge_path[-1]].append(element)
        for str_element in text:
            corpus_dict.update({knowledge_path[-1]: str_element})
        knowledge_path.pop(-1)
        object_list.clear()
        # Clearing object_dict and merging_g. We do it this way to avoid using too much memory.
        # Because we do not know how much news can come in, we decided to set the cap at 170 000, because the largest test set we have been given is 85 967, which was collected over 16 days.
        # By doubling this number, we estimate that we get news for 1 month before clearing, and because few news stories have a lifespan that long, we feel it is a reasonable timeframe.
        if len(object_dict.keys()) > 170000:
            for a in range(len(object_dict.keys())):
                x = object_dict.popitem()
                if x[0] in merging_g.keys():
                    del merging_g[x[0]]
        graph_maker()


# Checking if all graphs are ready for processing.
# This is only used when there are existing graphs in the knowledge_graph folder.
def checker():
    global element_count
    if len(object_dict) == 0:
        file_handler()
    if len(knowledge_path) == 0:
        element_count = len(object_dict.keys())
        print(f'All graphs are ready for processing. We have a total of {len(object_dict.keys())} graphs')
        new_incoming_graph()


def end_print():
    num_of_graph = (len([item for item in os.listdir('./MergingGraph') if
                         os.path.isfile(os.path.join('./MergingGraph', item))]))
    element_count = len(object_dict.keys())
    print(f"The total amount of files processed: {element_count}")
    print('Total new graph:', num_of_graph, 'and can now be found in the MergingGraph folder')
    for filename in os.listdir(merging_graph):
        graphs = os.path.join(merging_graph, filename)
        filesize = os.path.getsize(graphs)
        # The first removing of empty graphs, does not check the incoming graphs
        if filesize <= 2:
            empty_graph = graphs.replace('MergingGraph\\', 'knowledge_graph\\')
            del merging_g[empty_graph]
            del object_dict[empty_graph]
            os.remove(graphs)

    news_sitter()


# https://www.geeksforgeeks.org/python-join-tuples-if-similar-initial-element/
# Matching tuples.
# This function takes all incoming tuples and joins them to one big.
# E.g. f(('g1', 'g2'), ('g1', 'g3)) = ('g1', 'g2', 'g3)
def incoming_tuple_joiner():
    global similar_graph
    similar_graph = []
    for element in temp_sim_graph:
        if similar_graph and similar_graph[-1][0] == element[0]:
            similar_graph[-1].extend(element[1:])
        else:
            similar_graph.append([item for item in element])
    similar_graph = list(map(tuple, similar_graph))
    temp_sim_graph.clear()
    incoming_graph_creator(similar_graph[0])


arg_list = []


def graph_merging(var):
    global arg_list, ex_key
    g = Graph()
    for new in var:
        g += new
    # the new name is not random, it is the key to the graph. The key is always the first matching graph
    # Debian distros
    # name = arg_list[0].replace('knowledge_graph/', '').replace('.ttl', '')
    # Windows
    name = arg_list[0].replace('knowledge_graph\\', '').replace('.ttl', '')
    g.serialize(f'./MergingGraph/{name}.ttl', format='turtle')


# We cant know how many graphs that are matched, so by doing it this way we can create dynamic variables/graphs.
def incoming_graph_creator(*args):
    global ex_key, like, location, arg_list
    arg_list.clear()
    arg_list = list(args[0])
    like = []
    location = []
    # Checking if there are an existing graph with similar matches. If they are >= 30%, we want to merge them.
    for item in args[0]:
        for key, a_item in merging_g.items():
            if item in a_item[0]:
                like.append(item)
                like.append(key)
            ex_key = key
    if (len(like) / (len(args) + len(like))) >= 0.3:
        like.clear()
        incoming_g_finder()
    else:
        like.clear()
        for path in args:
            for loc in path:
                g = Graph()
                g.parse(location=loc, format="turtle")
                location.append(g)
        # merging_g stores the new graphs.
        key = args[0]
        merging_g[key[0]] = list(similar_graph)
        graph_merging(location)


def incoming_g_finder():
    global ex_key, arg_list, like
    temp = []
    # Finding the old name to the graph that is going to be extended
    # Debian distros
    # exsisting_name = ex_key.replace('knowledge_graph/', '').replace('.ttl', '').replace('-', ' ')
    # Windows
    exsisting_name = ex_key.replace('knowledge_graph\\', '').replace('.ttl', '').replace('-', ' ')
    temp.append(exsisting_name)
    for d in temp:
        to_del.append('./MergingGraph/' + d.replace(' ', '-') + '.ttl')

    new_val = {ex_key: list(map(tuple, similar_graph))}
    ny = new_val[ex_key]
    old = merging_g[ex_key]
    # Updating the new values to a graph
    if len(ny[0]) > len(old[0]):
        merging_g.update(new_val)

    location = []

    for i in like:
        arg_list.append(i)
        like.clear()
    if os.path.exists(to_del[0]):
        pass
    else:
        os.remove(to_del[0])
        to_del.clear()
        arg_list.insert(0, ex_key)
        for path in arg_list:
            g = Graph()
            g.parse(location=path, format="turtle")
            location.append(g)
        graph_merging(location)


def new_incoming_graph():
    global elementToCompare, elementToCompare2
    global elementToCompare, elementToCompare2
    elementToCompare = []
    elementToCompare2 = []

    for keys, value in object_dict.items():
        elementToCompare2.append(keys)

    elementToCompare.append(elementToCompare2.pop(0))

    for_incoming_graph()


# The model for matching graphs. The first evaluation is only on the graphs entities, we are using a text model, but only feed it the entities of two graphs.
def for_incoming_graph():
    knowledge_path.clear()
    for x in elementToCompare:
        for y in elementToCompare2:
            entity = object_dict.get(x)
            entity2 = object_dict.get(y)
            spacer = ' '.join(entity)
            spacer2 = ' '.join(entity2)
            if len(elementToCompare2) > 1:
                elementToCompare.pop(0)
                elementToCompare.append(elementToCompare2[0])
            graph = nlp(spacer)
            graph2 = nlp(spacer2)
            entity_similarity = graph.similarity(graph2)
            if entity_similarity >= 0.75:
                text_element = corpus_dict.get(x)
                text_element2 = corpus_dict.get(y)
                corpus = nlp(text_element)
                corpus2 = nlp(text_element2)
                text_similarity = corpus.similarity(corpus2)
                if text_similarity >= 0.78:
                    tfidf = vectorization.fit_transform([text_element, text_element2])
                    tfidf_similarity = (tfidf * tfidf.T)[0, 1]
                    if tfidf_similarity >= 0.18:
                        print(f'The graphs that are being compared {x, y}')
                        print(
                            f'{corpus}\n{corpus2}\nEntity score: {entity_similarity}'
                            f' Text spacy score: {text_similarity} Tf-idf model score:{tfidf_similarity}')
                        temp_sim_graph.extend([(x, y)])
    if len(temp_sim_graph) > 0:
        incoming_tuple_joiner()
    if len(elementToCompare2) == 0:
        end_print()
    else:
        print(f'There are {len(elementToCompare2)} elements left')
        elementToCompare2.pop(0)
        for_incoming_graph()


element = (len([item for item in os.listdir(knowledge_directory) if
                os.path.isfile(os.path.join(knowledge_directory, item))]))

# http://thepythoncorner.com/dev/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/
# https://pypi.org/project/watchdog/
# To monitor the folder we use watchdog, in the link above you can find the inspiration for this code lines.
if __name__ == "__main__":
    monitor_handler = PatternMatchingEventHandler(patterns='*', ignore_patterns='',
                                                  ignore_directories=False, case_sensitive=True)


def new_file_added(event):
    global element
    print('This file has been added', event.src_path)
    element = (len([item for item in os.listdir(knowledge_directory) if
                    os.path.isfile(os.path.join(knowledge_directory, item))]))
    knowledge_path.append(event.src_path)
    return element


def news_sitter(my_wacther=None):
    monitor_handler.on_created = new_file_added
    my_watcher = Observer()
    my_watcher.schedule(monitor_handler, knowledge_directory, recursive=True)
    my_watcher.start()
    print('Waiting for a new Graph.....')
    try:
        while True:
            time.sleep(1)
            if len(knowledge_path) > 1:
                graph_maker()
                new_incoming_graph()

    except KeyboardInterrupt:
        my_wacther.stop()
        my_wacther.join()


def terminal_menu():
    global user_input
    print('-' * 40, 'Welcome to NEWS SQUIRREL', '-' * 40)
    print(f"The purpose of this program is the parse smaller knowledge graph, and merging them in to bigger graphs. \n"
          'The program reads from the (knowledge_graph) directory, and will parse the new and bigger graph to the folder(MergingGraph) \n'
          'For every iteration, the new graph will be stored. Please make sure that (Merging Graph) is empty. This is to ensure that the end feedback is correct\n'
          'For optimal use case pleas make sure both folders are empty. Run the code type (1), and start the stream of incoming files.\n'
          'If you are using this without a stream of files. You can copy and past the file into (knowledge_graph), but do not select more than 250 files.\n'
          'For computers with lower processing power, do not add more than 80 files at once.\n'
          'The parsing will begin when more than two files has been added.\n\n'
          'Sub optimal, if the folder (knowledge_graph) contain files the program will run, and after parsing all the files. It will start monitoring for incoming files.\n\n'
          'WARNING: The recursion limit is currently sett to 5000, the recursion depth is proportional to the amount of files in your folder. \n\n'
          '- If this is a problem you will have to change it manually in the code - \n'
          '- The format for the files, is currently sett to turtle(.ttl). - \n\n'
          )
    print('-' * 50, 'Menu', '-' * 50)
    print(
        f'The current size of the folder is: {element} elements. If there are some empty files, they will be removed.\n')
    print('1. To Start')
    print('2. Exit')

    while True:
        try:
            user_input = int(input('Enter here (1-2): '))
            if user_input == 1:
                if element >= 2:
                    checker()
                else:
                    print(f'There are no graph in {knowledge_directory}, you are now in monitor mode.')
                    news_sitter()
            if user_input == 2:
                exit()
            if user_input > 2 or user_input < 1:
                print('Please enter a number between 1-2')
        except ValueError:
            print('Value is not accepted. Please type in a number between 1-2')


terminal_menu()
