# Notes for auditors and reviewers

- Please play close attention to the withdrawal function and flow - there have been a variety of issues with the final withdrawal as either funds are left over in the pool when they shouldnt be or their arent enough funds to service the final withdrawal resulting in an invalid amount error from the MCDEX protocol. In the latest iteration, this is fixed but would appreciate more attention to the entire withdrawal flow.

- Another potential area of concern is the funds generated between harvests that arent reflected when a withdrawal happens between a harvest. Resulting in the buffer to be inadvertantly increased, this doesnt present any immediate economic risks as a remargin can be called to amend this. But attention to this would be appreciated.

- Generally mcdex or uniswap protocol fees have been excluded from calculations by only using the final amount output by the specific trade function, if this is not the case anywhere please do notify us.