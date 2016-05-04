/**
 * Created by ejc84332 on 5/3/16.
 */

/** @jsx React.DOM */

var Modal = require('react-modal');

var ProgramResult = React.createClass({

    handleClick: function(e) {
        console.log('clicked!');
        console.log(this.props);
        if (typeof this.props.onClick === 'function') {
            this.props.onClick(this.props.tag);
        }
    },
    render: function() {
        var tag = this.props.tag;
        return (
            <tr onClick={this.handleClick} key={tag['id']}>
                <td>{tag['key']}</td>
                <td>{tag['tag']}</td>
                <td>{tag['outcome'] ? 'X': ''}</td>
                <td>{tag['topic'] ? 'X': ''}</td>
                <td>{tag['other'] ? 'X': ''}</td>
            </tr>
        );
    }
});

var ProgramSearch = React.createClass({

  // sets initial state
  getInitialState: function(){
    return { tagString: '', keyString: '', tags: [], showModal: false, currentTag: '' };
  },

  componentDidMount: function() {
    this.serverRequest = $.get(this.props.source, function (result) {
      var tags = result['tags'];
      this.setState({tags: tags});
    }.bind(this));
  },

  // sets state, triggers render method
  handleTagChange: function(event){
    this.setState({tagString:event.target.value});
  },

  // sets state, triggers render method
  handleKeyChange: function(event){
    this.setState({keyString:event.target.value});
  },

  close() {
    this.setState({ showModal: false });
  },

  open() {
    this.setState({ showModal: true });
  },

  handleClick: function(tag) {
    this.open();
    this.setState({ currentTag: tag['id'] });
  },

  render: function() {

    var tags = this.state.tags;
    var tagString = this.state.tagString.trim().toLowerCase();
    var keyString = this.state.keyString.trim().toLowerCase();

    if(tagString.length > 0 || keyString.length > 0){
        tags = tags.filter(function(tag){
            var ks = tag['key'].toLowerCase().match( keyString );
            var ts = tag['tag'].toLowerCase().match( tagString );
            if (ks && ts ){
                return tag;
            }
      });
    }

    return (
      <div>
        <label for="tag">Filter Tag:</label>
        <input type="text" name="tag" value={this.state.tagString} onChange={this.handleTagChange} placeholder="Filter Tag" />
        <label for="key">Filter Key:</label>
        <input type="text" name="key" value={this.state.keyString} onChange={this.handleKeyChange} placeholder="Filter Key" />
        <table>
            <thead>
                <tr>
                    <th>Key</th>
                    <th>Tag</th>
                    <th>Outcome</th>
                    <th>Topic</th>
                    <th>Other</th>
                </tr>
            </thead>
            <tbody>
                {
                    tags.map(function(tag){
                        return <ProgramResult key={tag['id']} tag={tag} onClick={this.handleClick} />
                    }, this)
                }
            </tbody>
        </table>
        <Modal
          isOpen={this.state.showModal}
          onRequestClose={this.close}
        >

          <h2 ref="subtitle">Hello</h2>
          <button onClick={this.close}>close</button>
          <div>I am a modal</div>
        </Modal>
      </div>
    )

  }

});

ReactDOM.render(
  <ProgramSearch source="http://127.0.0.1:5000/admin/programsearch/all"/>,
  document.getElementById('main')
);
