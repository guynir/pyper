# pyper

A simple pipeline implementation for the Python language.

The pipeline implements a basic Chain-of-Responsibilities pattern with some cool
extensions.

# Design

The pipeline implementation relies on the following constructs:

```
+-----+      +-------+      +-------+                  +------+
|     |      |       |      |       |                  |      |
| SRC | ---> | CMD#1 | ---> | CMD#2 | ---> ..... --->  | SINK |
|     |      |       |      |       |                  |      |
+-----+      +-------+      +-------+                  +------+
```

The pipeline has several concepts and roles:

* Command: a unit of execution called to complete a single task. Each command in a
  pipeline has a single role or responsibility.
* Source: An optional component that pumps data into the pipeline execution cycle.
* Sink: An optional that is always executed after each cycle to extract data and
  make it available to the outside caller.
* Pipeline: An implementation that orchestrates the calling of each element and
  managing its lifecycle.
* Context: An object that maintains the state of a pipeline cycle. In essence, it's
  a facility to share data among the tasks.
* Cycle: A behavior of the pipeline. A cycle is simple a process of taking the name
  data piece available by a `Source` and calling all `Command` objects following it.
  There may be several cycles of execution per execution.
* Pipeline execution: The process of pulling data from a source (if available) and
  executing a cycle for each piece of data.

# Example

A pipeline that takes a set of raw images and converts them into PNG format:

```
+--------+      +---------+      +-------+      +--------+
| Read   |      | Convert |      | Write |      | Write  |
| raw    | ---> | image   | ---> | log   | ---> | PNG    |
| images |      | to PNG  |      |       |      | image  |
+--------+      +---------+      +-------+      +--------+
```

The source reads raw images into memory. The source may read it from a file system,
remote web server or even a block storage, such as AWS S3.
For each image read, the 'Convert image to PNG' command will convert the raw image
in memory to PNG compressed representation.
The 'Write log' task may generate log information or audit logs.
The 'Write PNG image' will typically be a `Sink` (but may also be a `Command` if
the caller chooses to). The sink will write the file in PNG format a target
destination: it may be a local file system, remote web server, E-mail it or
even store it in block storage, such as AWS S3.

Each component has its own designated goal. We can replace the source or sink to
change the origin or destination, but the rest of the pipeline will behave the
same.

# Lifecycle

Each component (`Source`, `Command` and `Sink`) is lifecycle-aware. Which means that
each of these components will have a call to `setup()` method before pipeline
execution begins and `cleanup` after pipeline execution completes.

The method `handle` in each command is called to execute the command's specific
goal. If `Sink` exists as well, its `handle` method is also called.

# Code examples

```python

from pyper.pipeline import *

# Read all images from local file system.
source = ImageLoaderDataSource("/var/data/images")

# Write target images into ....
sink = ImageWriterSink("/tmp/images")

# Create a new pipeline.
pipeline = Pipeline(source, sink)

# A command that resize the image, if necessary to a fixed resolution.
pipeline.add_command(ImageResizeCommand(1024, 768))

# A command that adds a watermark to each image. 
pipeline.add_command(ImageWatermarkCommand("Copyright by ...."))

# A command that compress the raw image in memory.
pipeline.add_command(CompressImageCommand())

# Execute pipeline.
pipeline.run()
```
NOTE: We recommend importing the library objects via `from pyper.pipeline import *`
This will import all relevant objects automatically (instead of importing them
one by one).

# Dependencies

Each `Command` can define a list of requirements: what it expects previous commands (and optionally, the `Source`)
to provide it for proper behavior - via the `Command.requires` property.
It can also specify which properties it provides to the next commands in the chain via the `Command.provides` property.
