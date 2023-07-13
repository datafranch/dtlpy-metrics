# Scoring and metrics app

![Annotators confusion matrix](assets/annotators_matrix.png)

## Description

This app improves the efficiency of annotating data by improving annotation quality while reducing the time required to
produce them.

The components of this app are:

1. A Python function to calculate the consensus score for each item in a consensus task
2. A node that can be added to pipelines to calculate the consensus score when a task's consensus items are completed.

## Install App in a Project

When the app is published, a DPK ID is generated. This ID is used to install the app into a project.

```
dlp app install --dpk-id <DPK ID> --project-name <PROJECT_NAME>
```

## Tutorial and How-To

* Scores for a consensus task will be automatically calculated when this app is installed.

## Components and Integrations

### FaaS

* calculate_task_item_score
    * Description: This function takes items from a consensus task and calculates the consensus score for each item (
      i.e. the average agreement of annotations between all annotators).
    * Input:
        * consensus_task_id: id of the consensus task
        * save_plot: bool for saving the comparison matrix plot between annotators
    * Output:
        * item feature set for the consensus scores of each item evaluated for consensus
*
* put_scores_on_a_task
* put_scores_on_two_datasets
* evaluate_stuff
    * Output: summary_stats (can be a single number/score, a single graph, multiple graphs, or upload results to a
      shebang report)

## Contributions, Bugs and Issues - How to Contribute

We welcome anyone to help us improve this app.  
[Here's](CONTRIBUTING.md) a detailed instructions to help you open a bug or ask for a feature request


