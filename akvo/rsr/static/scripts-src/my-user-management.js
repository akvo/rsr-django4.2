/** @jsx React.DOM */

// Akvo RSR is covered by the GNU Affero General Public License.
// See more details in the license.txt file located at the root folder of the
// Akvo RSR module. For additional details on the GNU license please see
// < http://www.gnu.org/licenses/agpl.html >.

var ApproveModal,
    Button = ReactBootstrap.Button,
    CountryJobTitle,
    DeleteModal,
    DropDownItem,
    DropdownButton = ReactBootstrap.DropdownButton,
    Employment,
    EmploymentList,
    MenuItem = ReactBootstrap.MenuItem,
    Modal = ReactBootstrap.Modal,
    ModalTrigger = ReactBootstrap.ModalTrigger,
    Table = ReactBootstrap.Table,
    TriggerModal,
    UserTable,
    initial_data,
    i18n;

// CSRF TOKEN
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

InviteRow = React.createClass({displayName: 'InviteRow',
    getInitialState: function() {
        return {
            button_text: '+',
            button_style: 'success'
        };
    },

    handleRowClick: function() {
        if (this.state.button_style === 'success') {
            this.props.addRow();
            this.setState({
                button_text: 'x',
                button_style: 'danger'
            });
        } else {
            this.props.deleteRow(this.props.rowKey);
        }
    },

    render: function() {
        var orgs = organisation_data.map(function(org) {
            return (
                React.DOM.option( {key:org.id, value:org.id}, org.name)
            );
        });

        var groups = group_data.map(function(group) {
            return (
                React.DOM.option( {key:group.id, value:group.id}, group.name)
            );
        });

        return (
            React.DOM.tr( {className:"invite-row"}, 
                React.DOM.td(null, 
                    React.DOM.input( {className:"form-control", type:"email", placeholder:i18n.email_text, maxLength:"254", required:"required"} )
                ),
                React.DOM.td(null, 
                    React.DOM.select( {className:"form-control org-select", defaultValue:""}, 
                        React.DOM.option( {key:"", value:""}, i18n.select_org_text),
                        orgs
                    )
                ),
                React.DOM.td(null, 
                    React.DOM.select( {className:"form-control group-select", defaultValue:""}, 
                        React.DOM.option( {key:"", value:""}, i18n.select_group_text),
                        groups
                    )
                ),
                React.DOM.td(null, 
                    Button( {bsStyle:this.state.button_style, onClick:this.handleRowClick}, this.state.button_text)
                )
            )
        );
    }
});

InviteTable = React.createClass({displayName: 'InviteTable',
    getInitialState: function() {
        return {
            rowKey: 0
        };
    },

    componentDidMount: function() {
        if (this.isMounted()) {
            this.addRow();
        }
    },

    addRow: function () {
        this.setState({
            rowKey: this.state.rowKey + 1
        });

        var inviteTableBody = document.getElementById('invite-table').querySelector('tbody');
        var newRow = document.createElement('tr');
        newRow.setAttribute('id', 'row-' + this.state.rowKey);
        newRow.className = "invite-row";
        inviteTableBody.appendChild(newRow);
        React.renderComponent(InviteRow( {rowKey:this.state.rowKey, addRow:this.addRow, deleteRow:this.deleteRow} ), newRow);
    },

    deleteRow: function(rowKey) {
        var row = document.getElementById('row-' + rowKey);
        row.parentNode.removeChild(row);
    },

    render: function() {
        return (
            Table( {striped:true}, 
                React.DOM.thead(null, 
                    React.DOM.tr(null, 
                        React.DOM.th(null, i18n.email_text),
                        React.DOM.th(null, i18n.organisations_text),
                        React.DOM.th(null, i18n.group_text),
                        React.DOM.th(null,  " " )
                    )
                ),
                React.DOM.tbody(null,  " " )
            )
        );
    }
});


InviteModal = React.createClass({displayName: 'InviteModal',
    inviteApiCall: function(email, org, group) {
        if (email === "" || org === "" || group === "") {
            console.log('Not enough data');
        } else {
            // Create request
            var url = '/rest/v1/invite_user/?format=json';

            var request = new XMLHttpRequest();
            request.open('POST', url, true);
            request.setRequestHeader("X-CSRFToken", csrftoken);
            request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

            // TODO: emails with strange tokens (e.g. '+')
            var data = "user_data=" + JSON.stringify({
                email: email,
                organisation: org,
                group: group
            });

            request.send(data);
        }
    },

    sendInvite: function() {
        // TODO: change to React.js instead of javascript
        var inviteTable = document.getElementById('invite-table');
        var inviteRows = inviteTable.querySelectorAll('.invite-row');
        for (var i = 0; i < inviteRows.length; i++) {
            var inviteRow = inviteRows[i];
            var emailInput = inviteRow.querySelector('input').value;
            var orgInput = inviteRow.querySelector('.org-select').value;
            var groupInput = inviteRow.querySelector('.group-select').value;
            this.inviteApiCall(emailInput, orgInput, groupInput);
        }
    },

    render: function() {
        return this.transferPropsTo(
            Modal( {bsSize:"large", title:"Invite Users"}, 
                React.DOM.div( {className:"modal-body", id:"invite-table"}, 
                    InviteTable(null )
                ),
                React.DOM.div( {className:"modal-footer"}, 
                    Button( {onClick:this.props.onRequestHide}, i18n.close_text),
                    Button( {onClick:this.sendInvite, bsStyle:"success"}, i18n.invite_users_text)
                )
            )
        );
    }
});


DeleteModal = React.createClass({displayName: 'DeleteModal',
  deleteEmployment: function() {
    $.ajax({
      type: "DELETE",
      url: "/rest/v1/employment/" + this.props.employment.id + '/?format=json',
      success: function(data) {
        this.handleDelete();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },

  handleDelete: function() {
    this.props.onDeleteToggle();
  },

  render: function() {
    return this.transferPropsTo(
      Modal( {title:i18n.remove_user_text}, 
      React.DOM.div( {className:"modal-body"}, 
      i18n.remove_text + ' ' + this.props.employment.user.first_name + ' ' + this.props.employment.user.last_name + ' ' + i18n.from_text + ' ' + this.props.employment.organisation.name + '?'
      ),
      React.DOM.div( {className:"modal-footer"}, 
      Button( {onClick:this.props.onRequestHide}, i18n.close_text),
      Button( {onClick:this.deleteEmployment, bsStyle:"danger"}, i18n.remove_button_text)
      )
      )
    );
  }
});


ApproveModal = React.createClass({displayName: 'ApproveModal',
  approveEmployment: function() {
    $.ajax({
      type: "POST",
      url: "/rest/v1/employment/" + this.props.employment.id + '/approve/?format=json',
      success: function(data) {
        this.handleApprove();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },

  handleApprove: function() {
    this.props.onRequestHide();
    this.props.onApproveToggle();
  },

  render: function() {
    return this.transferPropsTo(
      Modal( {title:"Approve user"}, 
      React.DOM.div( {className:"modal-body"}, 
      i18n.approve_text + ' ' + this.props.employment.user.first_name + ' ' + this.props.employment.user.last_name + ' ' + i18n.at_text + ' ' + this.props.employment.organisation.name + '?'
      ),
      React.DOM.div( {className:"modal-footer"}, 
      Button( {onClick:this.props.onRequestHide}, i18n.close_text),
      Button( {onClick:this.approveEmployment, bsStyle:"success"}, i18n.approve_button_text)
      )
      )
    );
  }
});


TriggerModal = React.createClass({displayName: 'TriggerModal',
  getInitialState: function() {
    return {
      visible: false
    };
  },

  componentDidMount: function() {
    var approved = this.props.employment.is_approved;
    if (this.isMounted() && this.props.delete) {
      this.setState({
        visible: true
      });
    } else if (this.isMounted() && !this.props.delete) {
      this.setState({
        visible: !approved
      });
    }
  },

  onApprove: function() {
    this.setState({
      visible: false
    });
  },

  render: function() {
    if ( !this.state.visible ) {
      return React.DOM.span(null);
    }
    if (this.props.delete) {
      return (
      ModalTrigger( {modal:DeleteModal( {employment:this.props.employment, onDeleteToggle:this.props.onDeleteToggle} )}, 
      Button( {bsStyle:"danger", bsSize:"xsmall"}, "X")
      )
      );
    } else {
      return (
        ModalTrigger( {modal:ApproveModal( {employment:this.props.employment, onApproveToggle:this.onApprove} )}, 
        Button( {bsStyle:"success", bsSize:"xsmall"}, "√")
        )
      );
    }
  }
});

DropDownItem = React.createClass({displayName: 'DropDownItem',
  setGroup: function() {
    $.ajax({
      type: "POST",
      url: "/rest/v1/employment/" + this.props.employment_id + '/set_group/' + this.props.group.id + '/?format=json',
      success: function(data) {
        this.props.onSetGroup(this.props.group.name);
      }.bind(this),
      error: function(xhr, status, err) {
        this.props.onSetGroup(this.props.old_group);
      }.bind(this)
    });
  },

  handleSetGroup: function() {
    // Ugly jQuery hack to close dropdown
    $("div.btn-group").removeClass("open");

    this.props.loading(true);
    this.props.onSetGroup(React.DOM.i(null, i18n.loading_text));
    this.setGroup();
    this.props.loading(false);
  },

  render: function() {
    return (
      MenuItem( {eventKey:this.props.group.id, onClick:this.handleSetGroup}, this.props.group.name)
    );
  }
});


CountryJobTitle = React.createClass({displayName: 'CountryJobTitle',
  render: function() {
    var country = this.props.country;
    var job_title = this.props.job_title;
    if (country === null && job_title === "") {
      return (
        React.DOM.span(null, " ")
      );
    } else {
      var text = "(";
      if (job_title !== "") {
        text += job_title;
      }
      if (country !== null) {
        if (job_title !== "") {
          text += " ";
        }
        text += i18n.in_text + ' ' + country.name;
      }
      text += ")";
      return (
        React.DOM.span( {className:"small"}, text,"   ")
      );
    }
  }
});


Employment = React.createClass({displayName: 'Employment',
  getInitialState: function() {
    return {
      visible: true,
      button_title: '(' + i18n.none_text + ')',
      loading: false
    };
  },

  componentDidMount: function() {
    var group = this.props.employment.group;
    if (this.isMounted() && group !== null) {
      this.setState({
        button_title: group.name
      });
    }
  },

  isLoading: function(boolean) {
    this.setState({
      loading: boolean
    });
  },

  onDelete: function() {
    this.setState({visible: false});
  },

  setGroupName: function(group) {
    this.setState({
      button_title: group
    });
  },

  render: function() {
    var employment_id = this.props.employment.id;
    var setGroupName = this.setGroupName;
    var old_title = this.state.button_title;
    var loading = this.isLoading;
    var other_groups = this.props.employment.other_groups.map(function(group) {
      return (
        DropDownItem( {key:group.id, group:group, employment_id:employment_id,
        onSetGroup:setGroupName, old_group:old_title, loading:loading} )
      );
    });
    if ( !this.state.visible ) {
      return React.DOM.span(null);
    } else {
      return (
        React.DOM.span(null, 
        this.props.employment.organisation.name," ",
        CountryJobTitle( {country:this.props.employment.country, job_title:this.props.employment.job_title} ),
        DropdownButton( {title:this.state.button_title, disabled:this.state.loading}, other_groups), "    ",
        TriggerModal( {employment:this.props.employment, onDeleteToggle:this.onDelete, delete:true} ), "  ",
        TriggerModal( {employment:this.props.employment, onDeleteToggle:this.onDelete, delete:false} )
        )
      );
    }
  }
});

var EmploymentRow = React.createClass({displayName: 'EmploymentRow',
  render: function() {
    return (
      React.DOM.tr(null, 
      React.DOM.td(null, this.props.employment.user.email),
      React.DOM.td(null, this.props.employment.user.first_name),
      React.DOM.td(null, this.props.employment.user.last_name),
      React.DOM.td( {className:"text-right"}, 
          Employment( {key:this.props.employment.id, employment:this.props.employment} )
      )
      )
    );
  }
});


UserTable = React.createClass({displayName: 'UserTable',
  getInitialState: function() {
    return {
      employments: []
    };
  },

  componentDidMount: function() {
    var employments = this.props.source;
    if (this.isMounted()) {
      this.setState({
        employments: employments
      });
    }
  },

  render: function() {
    var employments_table = this.state.employments.map(function(employment) {
      return (
        EmploymentRow( {key:employment.id, employment:employment} )
      );
    });
    return (
      Table( {striped:true}, 
          React.DOM.thead(null, 
              React.DOM.tr(null, 
                  React.DOM.th(null, i18n.email_text),
                  React.DOM.th(null, i18n.first_name_text),
                  React.DOM.th(null, i18n.last_name_text),
                  React.DOM.th( {className:"text-right"}, i18n.organisations_text)
              )
          ),
          React.DOM.tbody(null, employments_table)
      )
    );
  }
});


InviteButton = React.createClass({displayName: 'InviteButton',
  render: function() {
    return (ModalTrigger( {modal:InviteModal(null )}, 
            Button( {title:"Invite Users"}, 
            React.DOM.i( {className:"glyphicon glyphicon-user"}), " +"
            )
            ));
  }
});


initial_employment_data = JSON.parse(document.getElementById("initial-employment-data").innerHTML);
organisation_data = JSON.parse(document.getElementById("organisation-data").innerHTML);
group_data = JSON.parse(document.getElementById("group-data").innerHTML);
i18n = JSON.parse(document.getElementById("user-management-text").innerHTML);

React.renderComponent(UserTable( {source:initial_employment_data} ),
                      document.getElementById('user_table'));
React.renderComponent(InviteButton( {organisations:organisation_data, groups:group_data}),
                      document.getElementById('invite_button'));
