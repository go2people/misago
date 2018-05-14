/* jshint ignore:start */
import React from 'react';
import * as actions from 'misago/reducers/thread';
import ajax from 'misago/services/ajax';
import snackbar from 'misago/services/snackbar';
import store from 'misago/services/store';
import {Subscription} from "./toolbar-bottom";

export default function(props) {
  console.log('LOAD!')
  return (
    <div className="btn-group">
      <button
        aria-expanded="false"
        aria-haspopup="true"
        className="btn btn-default dropdown-toggle btn-block btn-outline"
        data-toggle="dropdown"
        type="button"
      >
        <span className="material-icon">
          {getIcon(props.subscription)}
        </span>
        {getLabel(props.subscription)}
      </button>
      <Dropdown {...props} />
    </div>
  );
}

export function getIcon(subscription) {
  if (subscription === true) {
    return 'star';
  } else if (subscription === false) {
    return 'star_half';
  } else {
    return 'star_border';
  }
}

export function getLabel(subscription) {
  if (subscription === true) {
    return gettext("E-mail");
  } else if (subscription === false) {
    return gettext("Enabled");
  } else {
    return gettext("Disabled");
  }
}

export function Dropdown(props) {
  return (
    <ul className="dropdown-menu dropdown-menu-right">
      <Disable {...props} />
      <Enable {...props} />
      <Email {...props} />
    </ul>
  );
}

export class Disable extends React.Component {
  onClick = () => {
    if (this.props.subscription === null) {
      return;
    }

    update(this.props, null, 'unsubscribe');
  };

  render() {
    return (
      <li>
        <button className="btn btn-link" onClick={this.onClick}>
          <span className="material-icon">
            star_border
          </span>
          {gettext("Unsubscribe")}
        </button>
      </li>
    )
  }
}

export class Enable extends React.Component {
  onClick = () => {
    if (this.props.subscription === false) {
      return;
    }

    update(this.props, false, 'notify');
  };

  render() {
    return (
      <li>
        <button className="btn btn-link" onClick={this.onClick}>
          <span className="material-icon">
            star_half
          </span>
          {gettext("Subscribe")}
        </button>
      </li>
    )
  }
}

export class Email extends React.Component {
  onClick = () => {
    if (this.props.subscription === true) {
      return;
    }

    update(this.props, true, 'email');
  };

  render() {
    return (
      <li>
        <button className="btn btn-link" onClick={this.onClick}>
          <span className="material-icon">
            star
          </span>
          {gettext("Subscribe with e-mail")}
        </button>
      </li>
    )
  }
}

export function update(thread, newState, value) {
  const oldState = {
    subscription: thread.subscription
  };
  console.log(thread)
    console.log(newState)
    console.log(value)

  store.dispatch(actions.update({
    subscription: newState
  }));

  ajax.request("PATCH", thread.id + '/update/subscription/', {'newState': newState, 'value': value},
  ).then((finalState) => {
    console.log(store);
      console.log(actions);
      console.log(finalState);
    // store.dispatch(actions.update(finalState));
  }, (rejection) => {
    if (rejection.status === 400) {
      snackbar.error(rejection.detail[0]);
    } else {
      snackbar.apiError(rejection);
    }
    console.log('oldState');
    store.dispatch(actions.update(oldState));
  });
}