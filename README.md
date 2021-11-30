# pendo-config-automation

Automated way to publish rules for pages and features to Pendo.

This is the *only* way to add things to Pendo. If you do this manually in the application, they will be deleted by the automation at the next run.

## Documentation

There is deeper documentation for adding data in [data.md](/docs/data.md)

There is deeper documentation for developers in [developing.md](/docs/developing.md)


## Notes

### Stash list

This list is an automatically maintained list of the 'names' we have for each page and the IDs
for that page that are assigned Pendo side. This should be committed after runs to give us hints
about how things are changing over time, and provide a canonical record of objects the automation
maintains over time.

We *could* (but never have) use this to go back and reinstate a deleted or renamed object
that got a new ID. We could look and say the old ID for `_advisor - foo/bar` was $ID try to make a new
object with the same ID in Pendo (again we never have needed to do this).

The stash list is used by our scrubber to ensure that only things that are managed by automation
exists in the managed groups (groups that start with "_").

The stash list is also used by folks ingesting info from Pendo... to diff and figure out what needs to
be re-ingested.
