# QUIC Cardinality Estimator Tool Using HyperLogLog Algorithm


This tool is based on the work of Yousra Chabchoub, Georges Hebrail in their
article "Sliding HyperLogLog: Estimating Cardinality in a Data Stream over a
Sliding Window" (2010).

***

## Flags and Setup

```commandline
--help - Get a list of all flags.
```
```commandline
-m <n> or --memory <n> - Set the amount of memory buckets (LFPMs) in memory to n.
                         This number should be a power of 2 and higher or equal to 16.
                         Defaults to 64.
```
```commandline
-v or --verify - Print the actual cardinality to verify error rate.
```
```commandline
-f <path> or --file <path> - Capture from a .pcap (.pcapng) file instead of a live capture.
```
```commandline
-l <path> or --log <path> - Path to log file in which you would like to save your output.
                           Defaults to "<current_folder>\logs\log.txt".
```
```commandline
--src - Enable Small Range Correction with Linear Counting.
        For more information regarding Small Range Correction,
            please refer to the HyperLogLog article (2007).
```

***

## Usage

To run the estimator, run the [Cardinality Estimator](CardinalityEstimator.py) script with the relevant flags.
While the script is running you may enter a number of different inputs as commands.

* *exit* or *quit* - Exit the estimator
* *\<blank input\>* or *estimate* or *cardinality* - Output the cardinality since the estimator started
* *status* - Output the LFPMs contents
* *\<n\>* - Output the cardinality in the last n seconds

Your actions will be automatically logged in the log file set by the **-l** flag (or in the default log file).

**Important Note:** There is currently a problem with logging.

If you are reading from a file, please wait for the file to finish reading before exiting the estimator
(you will be notified when the file reading was finished by the estimator).

If you are using Live Capture, your actions will not be logged.

***

## References

1. [Sliding HyperLogLog: Estimating Cardinality in a Data Stream over a Sliding Window]("https://hal.archives-ouvertes.fr/hal-00465313/document")
by Yousra Chabchoub, Georges Hebrail; 2010.
2. [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
by Philippe Flajolet, Éric Fusy, Olivier Gandouet, Frédéric Meunier; 2007.