EDI Cancellation
================

This module adds the next features in the cancel process:

1. Button to cancel only in the SAT was added.
2. The cancel process in Odoo, only could be executed when the SAT status
   is cancelled.
3. Invoices in other period generate a revert in the journal entry related to
   leave the accountant in the invoice period.
4. The cancel process can not be executed if the invoice is paid.
5. Group to hide Odoo button to cancel was added.
6. New setting to enable the payment cancellation from previous periods with reversal moves.
7. Add group for users who can manage payments from previous periods.

Which is the new flow to cancel?
--------------------------------

A new button `(Request Cancelation)` was added on the invoice view, that
appear when the invoice is open and the `PAC status` is `Signed`

This new button when is press, send the CFDI to the PAC to try cancel it
in the SAT system. And do not allows to cancel the invoice in Odoo until
it was properly canceled in the SAT. (This is an automatic action that
execute the system)


On Payments:
You can enable the new setting *Accounting / Configuration / Settings/ Cancellation settings / Enable cancellation with reversal move*

Now from the same cancel process, the payments are checked to know if they are from a previous period or current period. 

If payment is from previous periods you can select the date and journal of this reversal entry 
and the cancellation will remove the reconciliation with related documents (like invoices, etc.)
and create a new reversal entry without tax lines or cash basis lines. 
Also if it's required, the cancel process for the CFDI related is called.


Which are the cases supported in this module?
---------------------------------------------

**Case 1**

+----------+---------+
| System   | State   |
+==========+=========+
| Odoo     | Open    |
+----------+---------+
| PAC      | Signed  |
+----------+---------+
| SAT      | Valid   |
+----------+---------+

This case is when the invoice is properly signed in the SAT system. To
cancel is necessary to press the button `Request Cancelation`, that will
to verify that effectively the CFDI is not previously canceled in the SAT
system and will to send it to cancel in the SAT.

After of request the cancelation, could be found the next cases:

*The cancel process was succesful*

+----------+------------+
| System   | State      |
+==========+============+
| Odoo     | Open       |
+----------+------------+
| PAC      | Cancelled  |
+----------+------------+
| SAT      | Valid      |
+----------+------------+

In this case, the system will execute the next actions:

1. An action will to update the PAC status (To Canceled).

2. A method will be called and will try to cancel the invoice in Odoo.


*The cancel process cannot be completed*

+----------+------------+
| System   | State      |
+==========+============+
| Odoo     | Open       |
+----------+------------+
| PAC      | To Cancel  |
+----------+------------+
| SAT      | Valid      |
+----------+------------+

In this case, the system wait for the PAC system, and will execute the next
action:

1. A method will be called to verify if the CFDI was properly cancelled in
the SAT system, and when the SAT status is `Cancelled` will try to cancel the
invoice in Odoo.

**Case 2**

+----------+------------+
| System   | State      |
+==========+============+
| Odoo     | Open       |
+----------+------------+
| PAC      | To Cancel  |
+----------+------------+
| SAT      | Valid      |
+----------+------------+

This case is the same that in the previous case when the cancel process
cannot be completed.

If the customer does not accept the CFDI cancelation, the cancel process
must be aborted and the invoice must be returned to signed. For this, was
added an action in the invoice `Revert CFDI cancellation`, that could be
called in the `Actions` of it.


**Case 3**

+----------+------------+
| System   | State      |
+==========+============+
| Odoo     | Open       |
+----------+------------+
| PAC      | To Cancel  |
+----------+------------+
| SAT      | Cancelled  |
+----------+------------+

The system executes a scheduled action that will cancel the invoice in Odoo,
and in that process, the PAC status must be updated to `Cancelled`.


**Case 4**

+----------+------------+
| System   | State      |
+==========+============+
| Odoo     | Cancel     |
+----------+------------+
| PAC      | Signed     |
+----------+------------+
| SAT      | Valid      |
+----------+------------+

The system executes a scheduled action that will check that the SAT status
continues `Valid` and if yes, the invoice must be returned to `Open`
(Without generate a new CFDI). For this:

1. If the invoice does not has a journal entry, a new will be generated and
the invoice state must be changed to `Open`.

2. If the journal entry in the invoice has a revert, it will be cancelled
and the invoice state must be changed to `Open`.

**Case 5**

+----------+------------+
| System   | State      |
+==========+============+
| Odoo     | Cancel     |
+----------+------------+
| PAC      | To Cancel  |
+----------+------------+
| SAT      | Valid      |
+----------+------------+

This is the same case that in the previous one, but extra after that the
invoice is open again, the PAC status must be updated to 'Signed.'

Bug Tracker
===========

Bugs are tracked on
`GitLab Issues <https://git.vauxoo.com/Vauxoo/mexico/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback.

Credits
=======

**Contributors**

* Nhomar Hernandez <nhomar@vauxoo.com> (Designer)
* Luis Torres <luis_t@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
