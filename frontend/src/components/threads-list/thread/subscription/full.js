/* jshint ignore:start */
import React from 'react';
import { patch } from 'misago/reducers/threads'; // jshint ignore:line
import ajax from 'misago/services/ajax'; // jshint ignore:line
import snackbar from 'misago/services/snackbar'; // jshint ignore:line
import store from 'misago/services/store'; // jshint ignore:line

/* jshint ignore:start */
const STATE_UPDATES = {
  'unsubscribe': null,
  'notify': false,
};

export default class extends React.Component {

    /* jshint ignore:start */
  setSubscription = (newState) => {
    this.setState({
      isLoading: true
    });

    let oldState = this.props.thread.subscription;

    store.dispatch(patch(this.props.thread, {
      subscription: STATE_UPDATES[newState]
    }));

    ajax.request("PATCH", this.props.thread.id + '/update/subscription/', {'newState': newState, 'value': newState}
    ).then(() => {
      this.setState({
        isLoading: false
      });
    }, (rejection) => {
      this.setState({
        isLoading: false
      });
      store.dispatch(patch(this.props.thread, {
        subscription: STATE_UPDATES[oldState]
      }));
      snackbar.apiError(rejection);
    });
  };

  changeValue = () => {
    const subscription = this.props.thread.subscription;
    if ('subscription2' in this) {
      this.subscription2 = !this.subscription2;
    } else {
      this.subscription2 = subscription === false || subscription === true;
    }

    if (this.subscription2) {
      this.setSubscription('unsubscribe');
    } else {
      this.setSubscription('notify');
    }
  };

  render() {
    const subscription = this.props.thread.subscription;
    const subscription2 = subscription === false || subscription === true;
    let className = 'col-xs-12';
    className += ' hidden-xs hidden-sm';

    if (this.props.thread.subcategories.length !== 0) {
      return (<span className="fa fa-chevron-down"></span>);
    }

    return (
      <div className={className}>
        <div className="btn-group btn-group-justified form-group">
          <div className="btn-group checkbox">
            <label
                htmlFor={"melding" + this.props.thread.id}>
              <input
                type="checkbox"
                defaultChecked={subscription2}
                id={'melding' + this.props.thread.id}
                name={'melding'}
                onClick={this.changeValue}
              >
              </input>
              Meldingen ontvangen?
            </label>
          </div>
        </div>
      </div>
    );
  }
}
