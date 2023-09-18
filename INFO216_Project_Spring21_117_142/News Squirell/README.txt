# News Squirrel

News Squirrel is a News graph aggregator, it can take a stream of smaller news graphs in the Turtle format(.ttl).
Identify groups of graphs that represent or closely related events. It then merges the similar graphs to a bigger graphs.
The new graph is stored in the 'MergingGraph' directory, for the incoming graph's. They have to be added in the folder
'knowledge_graph'. For the optimal use case both 'MergingGraph' and 'knowledge_graph' should be empty,
then run the program and start adding in graphs. The program is intended for a feed of graph,
if you are going to copy and paste files in to 'knowledge_graph' do not copy more than 250 files. It can crash. 
Files should not be added while the processing has begun. Computers with lower processing power should not add more than
80 files at once.

If the folder 'knowledge_graph' has files in it, the program will run as intended, And when the program is done
all files form the 'knowledge_graph' folder. The program will start monitoring for new graphs. 


### Prerequisites

    pip install -r requirements.txt
            
## Usage

Optimal run case:

For optimal use case pleas make sure both folders are empty. Run the code hit (1), 
and start the stream of incoming files. If you are using this without a stream of files.
You can copy and past the file into 'knowledge_graph', but do not select more than 250 files.
The parsing will begin when more than two files has been added. 
The folder test_sett, include a test set. 
Run the code, type 1 and when you see 'Waiting for a new Graph'.
Copy all files from test_set and paste them in to the 'knowledge_graph'.  

Sub optimal:

If the folder 'knowledge_graph' contain files the program will run, and after parsing all the files.
It will start monitoring for incoming files.    


If recursion depth becomes an issue, this can be altered at the top of the python program. 
"sys.setrecursionlimit(5000)" - change from 5000 to the value you want.


### Acknowledgements

##### Watchdog
http://thepythoncorner.com/dev/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/
https://pypi.org/project/watchdog/

##### Tuple joiner
https://www.geeksforgeeks.org/python-join-tuples-if-similar-initial-element/

### GitHub repository

The project will be available at the end of summer.
https://github.com/Tobbelobby/News_Squirrel.git
